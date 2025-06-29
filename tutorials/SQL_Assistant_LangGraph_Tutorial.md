# 🛠️ Build a Trustworthy Multi-Agent SQL Assistant with LangGraph, LangChain & GPT-4o-mini

> **Author**: Google SDE III (AI Engineering) – open-sourced for the community  
> **Repo purpose**: Demonstrates a production-grade pattern for human-in-the-loop, cost-aware LLM agents that translate natural-language questions into safe, optimized SQL.

---

## Table of Contents
1. [Why this project?](#why-this-project)
2. [Architecture at a glance](#architecture-at-a-glance)
3. [Quick start](#quick-start)
4. [Project layout](#project-layout)
5. [Step-by-step walkthrough](#step-by-step-walkthrough)
   * 5.1 [Spin-up an example SQLite DB](#51-spin-up-an-example-sqlite-db)
   * 5.2 [Define agents with LangChain](#52-define-agents-with-langchain)
   * 5.3 [Model the workflow graph in LangGraph](#53-model-the-workflow-graph-in-langgraph)
   * 5.4 [Token & cost accounting](#54-token--cost-accounting)
   * 5.5 [Streamlit human checkpoint UI](#55-streamlit-human-checkpoint-ui)
6. [Running locally](#running-locally)
7. [Docker deployment](#docker-deployment)
8. [Extending to large schemas with RAG](#extending-to-large-schemas-with-rag)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap](#roadmap)
11. [License](#license)

---

## Why this project?
Large-language-model agents can now write SQL, but real-world teams worry about **hallucinated columns, runaway costs, and privacy leaks**.  This repo shows how to:

* Chain **three specialised GPT-4o-mini agents** (Generation → Review → Compliance) in a **LangGraph** DAG for deterministic execution.
* Insert a **human-in-the-loop checkpoint** between Generation & Review, giving users veto power.
* Track **token usage & $ cost** for every step.
* Expose everything through a clean **Streamlit** interface.

The end result is a lightweight, reproducible template that you can fork for Postgres, BigQuery, Snowflake, etc.

---

## Architecture at a glance
```text
┌───────────────┐      ┌───────────────┐      ┌──────────────────┐
│ NL ↦ SQL Gen  │ ───▶ │  SQL Reviewer │ ───▶ │ Compliance Guard │
└───────────────┘      └───────────────┘      └──────────────────┘
        ▲                        │                     │
        │                        │                     ▼
        │                  (Human-approved)         SQLite
        │                                             ▲
 Streamlit UI  ◀──────── token + $ telemetry ─────────┘
```
* **LangChain** provides the `ChatOpenAI` wrapper and parser helpers.  
* **LangGraph** wires the three agents plus a conditional edge that fires only when the user clicks **✅ Confirm**.  
* **SQLite** stands in for your real warehouse; swapping drivers is trivial.

---

## Quick start
```bash
# 1 – clone & install
$ git clone https://github.com/<you>/sql-assistant-langgraph.git
$ cd sql-assistant-langgraph
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 2 – set creds
$ export OPENAI_API_KEY="sk-..."

# 3 – run the demo app
$ streamlit run app.py
```
Navigate to <http://localhost:8501>, ask a question like **“Top 5 products by revenue since April 2024”**, inspect the generated SQL, then hit **Confirm & Review**.

---

## Project layout
```
.
├── app.py                # Streamlit UI
├── graph.py              # LangGraph DAG definition
├── agents.py             # Agent roles, goals & prompts
├── tasks.py              # Callable task functions
├── data/
│   └── sample_db.sqlite  # Example dataset
├── utils/
│   ├── db.py             # Schema helpers & query runner
│   └── cost.py           # Token/cost extraction
├── README.md             # ✨ you’re here
└── requirements.txt      # LangChain, LangGraph, Streamlit, etc.
```

---

## Step-by-step walkthrough

### 5.1 Spin-up an example SQLite DB
```python
# utils/db.py
import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent.parent / "data" / "sample_db.sqlite"

def init_db():
    \"\"\"Create tables & seed mock data for reproducibility.\"\"\"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # create & populate tables (products, customers, orders, order_items…)
```
Run once:
```bash
python -m utils.db  # creates/overwrites sample_db.sqlite
```

### 5.2 Define agents with LangChain
```python
# agents.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

LLM = lambda: ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def query_generator():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Data Analyst…"),
        ("human",  "{user_input}\\n\\nSCHEMA:\\n{db_schema}")
    ])
    return prompt | LLM()

# Similar wrappers for reviewer() and compliance_guard()
```
Each function returns a **Runnable**—the building block that LangGraph nodes can execute.

### 5.3 Model the workflow graph in LangGraph
```python
# graph.py
from langgraph.graph import StateGraph, END
from agents import query_generator, reviewer, compliance_guard

Graph = StateGraph()

# Nodes
Graph.add_node("generate",   query_generator())
Graph.add_node("review",     reviewer())
Graph.add_node("compliance", compliance_guard())

# Edges
Graph.add_edge("generate", "review")        # auto after Confirm
Graph.add_edge("review", "compliance")
Graph.add_edge("compliance", END)            # finish

app_graph = Graph.compile()
```
The `generate → review` edge is **conditional**; `app.py` only triggers it after the user hits **Confirm**.  LangGraph keeps track of intermediate outputs so downstream nodes (`compliance`) can access the reviewed SQL.

### 5.4 Token & cost accounting
```python
# utils/cost.py
PRICE_IN   = 0.00015   # $/1K prompt tokens (gpt-4o-mini)
PRICE_OUT  = 0.00060   # $/1K completion tokens

def usd_cost(usage: dict) -> float:
    return usage["prompt_tokens"] / 1_000 * PRICE_IN + \\
           usage["completion_tokens"] / 1_000 * PRICE_OUT
```
Every runnable returns `{"text": …, "usage": {prompt_tokens, completion_tokens}}`.  The Streamlit sidebar tallies `session_state["llm_cost"] += usd_cost(usage)`.

### 5.5 Streamlit human checkpoint UI
```python
# app.py (excerpt)
if st.button("Generate SQL"):
    gen_out = app_graph.invoke("generate", {
        "user_input": prompt,
        "db_schema": schema
    })
    st.session_state["draft_sql"] = gen_out["text"]
    st.session_state["draft_usage"] = gen_out["usage"]

if st.session_state.get("draft_sql"):
    st.code(format_sql(st.session_state["draft_sql"]))
    col1, col2 = st.columns(2)
    if col1.button("✅ Confirm & Review"):
        review_out     = app_graph.invoke("review", {"sql": st.session_state["draft_sql"], "db_schema": schema})
        compliance_out = app_graph.invoke("compliance", {"sql": review_out["text"]})
        # …render outputs & cost…
```

---

## Running locally
1. `python utils/db.py` – seed the DB.  
2. `streamlit run app.py` – open http://localhost:8501.  
3. Ask questions; watch cost meter.

### Tests
```bash
pytest tests/  # basic unit tests for each node
```

---

## Docker deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV OPENAI_API_KEY="change_me"
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--browser.serverAddress", "0.0.0.0"]
```
```bash
# build & run
$ docker build -t sql-assistant .
$ docker run -p 8080:8080 -e OPENAI_API_KEY=$OPENAI_API_KEY sql-assistant
```

---

## Extending to large schemas with RAG
* Replace `get_structured_schema()` with a **vector-store retriever** (e.g., FAISS + sentence-transformers) that returns only tables relevant to the user intent.
* Stream results into the prompt via LangChain’s `ContextualCompressionRetriever`.

---

## Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Empty results | Query filters wrong date range | Lower `temperature`, refine `reviewer()` prompt |
| Cost spikes | Loops / retries | Add LangGraph `retry` policy & max_depth |
| \"no such column\" error | Hallucination slipped past reviewer | Strengthen schema validation logic |

---

## Roadmap
- 🔄  Asynchronous edge execution for non-blocking UI.  
- 🛡️  Policy-based guardrails (OpenAI JSON mode).  
- ☁️  Terraform + Cloud Run one-click deploy.

---

## License
MIT © 2025 Google SDE III
