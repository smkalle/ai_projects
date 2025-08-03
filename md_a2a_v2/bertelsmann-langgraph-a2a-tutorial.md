
# Bertelsmann‑Style Multi‑Agent Content Search with LangGraph (A2A Edition)

> Production‑grade, hands‑on tutorial for AI engineers to build a decentralized, agent‑to‑agent (A2A) content search system across Books, TV, and News — inspired by Bertelsmann’s Content Search and implemented with **LangGraph**.

**Last updated:** 2025-08-03 03:08 UTC  
**Tested on:** Python 3.10+

---

## Why this guide

Bertelsmann’s AI Hub built a **production multi‑agent system** with LangGraph that lets creatives ask natural‑language questions like *“What documentaries do we have on renewable energy?”* and get unified answers across decentralized sources (books, TV, news). This tutorial shows **how to build your own** version — and upgrades it with **A2A (Agent‑to‑Agent)** handoffs so agents collaborate **without a central supervisor**.

---

## What you’ll build

- A **network architecture** of specialized agents: `publishing`, `broadcasting`, `news`  
- **A2A handoffs** using `Command(goto=...)` + shared state (messages)  
- Domain **tools** (mocked first, then swappable for real data/APIs)  
- An **end‑to‑end graph** that routes queries in seconds, not hours

---

## Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful graphs for LLM apps  
- [LangGraph Prebuilt](https://github.com/langchain-ai/langgraph/tree/main/python/langgraph-prebuilt) — ready agents (ReAct, supervisor)  
- [LangGraph Swarm](https://github.com/langchain-ai/langgraph-swarm-py) — optional swarm helper for emergent multi‑agent collab  
- [langchain-openai](https://github.com/langchain-ai/langchain/tree/master/libs/partners/openai) — OpenAI chat models

---

## Quickstart

```bash
# 1) Create a fresh env
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# 2) Install deps
pip install -U langgraph langgraph-prebuilt langchain-openai pydantic python-dotenv

# 3) Configure API key
echo "OPENAI_API_KEY=sk-..." > .env
```

> If you use Azure OpenAI, also set `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, and configure `ChatOpenAI` accordingly.

---

## Project layout

```
multiagent-a2a/
├─ app.py                 # run an interactive demo
├─ agents/
│  ├─ publishing.py
│  ├─ broadcasting.py
│  ├─ news.py
│  └─ tools.py
├─ graph.py               # LangGraph assembly (nodes, edges)
├─ data/                  # (optional mock data / adapters)
├─ .env.example
└─ README.md
```

---

## 1) Define domain tools

Start with mocked tools; you’ll swap real data sources later.

```python
# agents/tools.py
from langchain_core.tools import tool

@tool
def search_books(query: str) -> list[str]:
    """Search for books related to the query."""
    return [f"Book about {query}", f"Another book about {query}"]

@tool
def search_tv(query: str) -> list[str]:
    """Search for TV content related to the query."""
    return [f"TV show about {query}", f"Documentary about {query}"]

@tool
def search_news(query: str) -> list[str]:
    """Search for news articles related to the query."""
    return [f"News article about {query}", f"Another news article about {query}"]
```

---

## 2) Enable A2A handoffs

In LangGraph, agents return a `Command` to choose the **next agent** and update **shared state**.

```python
# agents/tools.py (continued)
from langgraph.types import Command
from langchain_core.tools import tool

@tool
def handoff(next_agent: str):
    """Hand off control to another agent by name (A2A)."""
    return Command(goto=next_agent)  # optional: update={{"messages": [...]}}
```

---

## 3) Build specialized agents

Use the **prebuilt ReAct agent** and give each agent only **its own tools** plus the `handoff` tool.

```python
# agents/publishing.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_books, handoff

model = ChatOpenAI(model="gpt-4o-mini")  # swap to your preferred model

PUBLISHING_PROMPT = """
You are the Publishing agent. Use search_books for book queries.
If the user asks for TV, films, or documentaries -> hand off to 'broadcasting'.
If the user asks for news or journalism -> hand off to 'news'.
Always explain *why* you handed off in one short sentence.
"""

publishing_agent = create_react_agent(
    model,
    tools=[search_books, handoff],
    prompt=PUBLISHING_PROMPT,
)
```

```python
# agents/broadcasting.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_tv, handoff

model = ChatOpenAI(model="gpt-4o-mini")

BROADCASTING_PROMPT = """
You are the Broadcasting agent. Use search_tv for TV/films/docs.
If it's books -> hand off to 'publishing'. If it's news -> 'news'.
"""

broadcasting_agent = create_react_agent(
    model,
    tools=[search_tv, handoff],
    prompt=BROADCASTING_PROMPT,
)
```

```python
# agents/news.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .tools import search_news, handoff

model = ChatOpenAI(model="gpt-4o-mini")

NEWS_PROMPT = """
You are the News agent. Use search_news for journalism.
If it's books -> 'publishing'. If it's TV -> 'broadcasting'.
"""

news_agent = create_react_agent(
    model,
    tools=[search_news, handoff],
    prompt=NEWS_PROMPT,
)
```

---

## 4) Assemble the graph (network)

A **Network** lets **any agent call any other** through A2A handoffs.

```python
# graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.types import Command

# import agents
from agents.publishing import publishing_agent
from agents.broadcasting import broadcasting_agent
from agents.news import news_agent

class AppState(MessagesState):
    pass  # use MessagesState for shared 'messages' by default

def as_node(agent_graph):
    # adapters to wrap prebuilt agents as callable nodes
    def _node(state: AppState) -> Command:
        result = agent_graph.invoke(state)
        return result  # may be a Command from handoff tool, or final ToolMessage
    return _node

builder = StateGraph(AppState)
builder.add_node("publishing", as_node(publishing_agent))
builder.add_node("broadcasting", as_node(broadcasting_agent))
builder.add_node("news", as_node(news_agent))

# Pick an entry point (can be any). Agents can re‑route via Command(goto=...)
builder.add_edge(START, "publishing")

app = builder.compile()
```

---

## 5) Run the demo

```python
# app.py
import os
from dotenv import load_dotenv
from graph import app

load_dotenv()

query = "What documentaries exist on renewable energy?"
state = {"messages": [{"role": "user", "content": query}]}

response = app.invoke(state)
print(response)
```

Run it:

```bash
python app.py
```

You should see the graph **start at `publishing`** and **hand off to `broadcasting`** for documentaries, returning a coherent answer. Try: *“Find books on renewable energy and any related news articles”* — the agents will cooperatively **hand off** until all domains are covered.

---

## 6) Swap in real data (production adapters)

Replace mocked tools with real interfaces. Examples:

- **Books (vector search)** — Qdrant, PGVector, or Elastic
- **TV** — internal MAM/archive APIs, metadata DBs
- **News** — newsroom CMS search or search APIs

Pattern:

```python
# agents/tools.py (real adapter sketch)
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant

# vectorstore = Qdrant.from_documents(..., OpenAIEmbeddings())  # index once

@tool
def search_books(query: str) -> list[str]:
    # results = vectorstore.similarity_search(query, k=5)
    # return [doc.page_content for doc in results]
    ...
```

---

## 7) Observability & guardrails

- **Tracing & evals**: Use [LangSmith](https://smith.langchain.com/) to trace, replay, and regression‑test agent flows.  
- **Safety**: Wrap tools with input validation; constrain tool schemas; add allow‑lists.  
- **Latency**: Parallelize domain calls where feasible. Cache frequent queries.  
- **Cost**: Use smaller models for routing; reserve larger models for synthesis.  
- **State**: Persist `MessagesState` for follow‑ups; trim long histories.

---

## 8) Architecture choices at a glance

| Architecture | Control | A2A | When to use |
|---|---|---|---|
| **Network** | Agents decide next via `Command(goto=...)` | **Yes** | Decentralized domains, emergent collab |
| **Supervisor** | Central router chooses agents | No | Clear routing policy, simpler ops |
| **Hierarchical** | Teams with supervisors | Partial | Very large orgs / team boundaries |

---

## 9) Extensions

- **Swarm mode**: Add [LangGraph Swarm](https://github.com/langchain-ai/langgraph-swarm-py) to let agents self‑select and resume with the last active agent.  
- **Human‑in‑the‑loop**: Insert approval nodes for sensitive queries.  
- **MCP/Tools**: Expose each agent as an API so divisions can embed the same agent in their own UIs.  
- **Studio**: Use LangGraph Studio to visualize runs and edges.

---

## 10) Production checklist

- [ ] Pydantic schemas for all tools  
- [ ] Timeouts/retries/circuit breakers around external systems  
- [ ] Structured outputs for routing (`next_agent`)  
- [ ] Canary + evals before enabling new agents  
- [ ] RBAC on tools and per‑division agents

---

## FAQ

**Does A2A require a supervisor?**  
No. Any agent can hand off to another via `Command(goto=...)`. Supervisors are optional.

**Can agents “loop” on a task together?**  
Yes. Agents can return `Command` to re‑enter themselves or each other until a stopping condition is met.

**Where do we add synthesis?**  
Add a final aggregation agent or a deterministic node that merges partial results into a single answer.

---

## References & further reading

- Bertelsmann × LangGraph case study (production deployment, impact): https://blog.langchain.com/customer-bertelsmann/  
- LangGraph multi‑agent concepts (handoffs, network, supervisor): https://langchain-ai.github.io/langgraph/concepts/multi_agent/  
- Prebuilt agents & 0.3 release notes: https://blog.langchain.com/langgraph-0-3-release-prebuilt-agents/  
- LangGraph Swarm (A2A‑style collaboration helpers): https://github.com/langchain-ai/langgraph-swarm-py  
- Changelog: LangGraph Swarm announcement: https://changelog.langchain.com/announcements/langgraph-swarm-for-building-multi-agent-systems

---

## License

MIT — do whatever helps your team ship safely and fast.
