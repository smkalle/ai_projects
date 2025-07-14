
# Building an AI Headhunter Agent with **LangGraph** & **Davia**

*Automate LinkedIn talent sourcing with a state‑aware, real‑time AI recruiter*

---

## Why this matters
| Metric | Evidence | Source |
|--------|----------|--------|
| 20 % faster hiring | AI‑driven recruitment vs. traditional | *Journal of Business Research*, 2023 |
| 15 % surge in demand | Tech‑enabled hiring tools | *ILO Report*, 2024 |
| 30 % efficiency gain | Parallel multi‑agent workflows | IEEE, 2022 |

---

## 1  Prerequisites

* Python ≥ 3.9  
* OpenAI & Tavily API keys  
* `git`, `make` (optional)  

Install core libs:
```bash
pip install davia langchain-openai langchain-community tavily-python
```

---

## 2  Project layout
```text
ai-headhunter/
├─ .env.example
├─ langgraph.json
├─ requirements.txt
└─ src/
   ├─ models.py
   ├─ agent.py
   └─ __main__.py
```

---

## 3  Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your keys
```

`.env.example`
```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

---

## 4  Domain model – `src/models.py`
```python
from dataclasses import dataclass

@dataclass
class Candidate:
    name: str
    title: str
    company: str
    location: str
    linkedin: str
    reason: str
```

---

## 5  LinkedIn search tool – `src/agent.py`
```python
from langchain_community.tools.tavily_search import TavilySearchResults
from .models import Candidate

tavily = TavilySearchResults(max_results=15, include_domains=["linkedin.com"])

def find_candidates(keyword: str) -> list[Candidate]:
    hits = tavily.run(keyword)
    out = []
    for h in hits:
        name, *rest = h.title.split(" - ")
        out.append(
            Candidate(
                name=name,
                title=" / ".join(rest),
                company="",
                location="",
                linkedin=h.url,
                reason=f"Matched '{keyword}'"
            )
        )
    return out
```

---

## 6  Chat node

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
```

```python
def chat_node(state):
    user_msg = state[-1]
    rsp = llm.invoke([user_msg])
    return state + [rsp]
```

---

## 7  Wire with **LangGraph**
```python
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated, List

State = Annotated[List[HumanMessage | AIMessage], MessagesState]

graph = StateGraph()
graph.add_node("chat", chat_node)
graph.add_node("search", search_node)
graph.set_start("chat")

# Route: if prompt contains 'search' → search node
graph.add_edge("chat", "search",
               condition=lambda s: "search" in s[-1].content.lower())
graph.add_edge("search", "chat")
```

---

## 8  Expose graph via **Davia** – `src/__main__.py`
```python
from davia import app
from .agent import graph as _graph

@app.graph
def hr():
    return _graph
```

`langgraph.json`
```json
{
  "dependencies": ["."],
  "graphs": {
    "hr": "src.agent:graph"
  }
}
```

---

## 9  Run locally

```bash
davia dev
```

Go to <http://localhost:8000>, type:  
`search senior machine‑learning engineer Seattle`  
– watch the streaming list of candidates.

---

## 10  Speed‑up with parallel search
```python
import asyncio

async def gather_candidates(queries):
    tasks = [asyncio.to_thread(find_candidates, q) for q in queries]
    results = await asyncio.gather(*tasks)
    return [c for sub in results for c in sub]
```

---

## 11  Deploy options

| Platform | Command |
|----------|---------|
| LangGraph Cloud | Push repo, set secrets |
| Vercel/Fly.io | `davia build --prod` → deploy |
| Kubernetes | Build Dockerfile, helm chart |

---

## 12  Security checklist
* Respect LinkedIn ToS (official API or consented scraping).  
* Encrypt stored PII.  
* Log prompts via **LangSmith** for audit.

---

## 13  Next steps
* Switch to OpenAI function‑calling → JSON output.  
* Add scoring/ranking node.  
* Write to Postgres or Supabase.  
* Auto‑message candidates via email/InMail.

---

## References
1. *Journal of Business Research* 2023 – AI hiring study.  
2. ILO World Employment Report 2024 – tech‑enabled recruitment stats.  
3. IEEE Multi‑Agent Systems Survey 2022 – parallel efficiency gains.  
4. Davia Docs – <https://docs.davia.dev>  
5. LangGraph Guide – <https://docs.langchain.com/langgraph>
