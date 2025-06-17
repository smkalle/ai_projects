# Agentic GraphRAG MVP – Legal Contract Analysis

> Leverage LLM‑powered structured extraction + Neo4j graph RAG + LangGraph agentic workflow + FastAPI streaming + React chat UI.

---

## ✨ Project Goal

Build an **end‑to‑end Graph Retrieval‑Augmented Generation (GraphRAG)** MVP that:

1. **Extracts** structured facts from contract text with **Gemini**.  
2. **Stores** that data in a **Neo4j** knowledge graph.  
3. **Queries** the graph through a **LangGraph** agent equipped with a custom `ContractSearch` tool.  
4. **Serves** chat answers via a **FastAPI** backend (Server‑Sent Events).  
5. **Displays** answers in a minimalist **React + Vite** web interface.

---

## 🏛️ Core Architecture

```
┌─────────────┐        Cypher          ┌───────────────┐
│   React UI  │ ───── REST+SSE ─────► │   FastAPI     │
│  (Vite)     │ ◄───────────────┐     │  LangGraph    │
└─────────────┘                 │     └───────┬───────┘
                                │             │
                                ▼             ▼
                          LangGraph Agent  Google Gemini
                                │
                                ▼
                             Neo4j DB  (public read‑only demo)
```

---

## 🚦 Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| **Python** | 3.9+ | FastAPI & LangGraph |
| **Node.js** | 18+ | React‑Vite front‑end |
| **Git** | latest | clone template |
| **Google AI Key** | Gemini & Embeddings | Create in **AI Studio** |

---

## 1 · Project Bootstrap

```bash
# folder scaffold
mkdir agentic-graphrag-mvp && cd $_
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 1.1 Backend

```bash
mkdir backend && cat > backend/requirements.txt <<'REQ'
fastapi
uvicorn[standard]
langchain
langgraph
langchain-google-genai
neo4j
pydantic
python-dotenv
sse-starlette
REQ

pip install -r backend/requirements.txt
```

### 1.2 Frontend

```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install && cd ..
```

---

## 2 · Configuration

Create **backend/.env**

```env
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

Neo4j public demo (read‑only):

```text
URI      = neo4j+s://demo.neo4jlabs.com
USER     = legalcontracts
PASSWORD = legalcontracts
DATABASE = legalcontracts
```

---

## 3 · Backend Code

<details>
<summary><code>backend/tools.py</code> – ContractSearch Tool</summary>

```python
# abridged
class ContractSearchTool(BaseTool):
    name = "ContractSearch"
    ...
    def _run(self, **kwargs):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        driver = GraphDatabase.driver(
            "neo4j+s://demo.neo4jlabs.com",
            auth=("legalcontracts", "legalcontracts")
        )
        # dynamic Cypher generation …
```
</details>

<details>
<summary><code>backend/agent.py</code> – LangGraph Workflow</summary>

```python
def create_agent_graph():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    tools = [ContractSearchTool()]
    agent = llm.bind_tools(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", lambda s: agent_node(s, agent, "agent"))
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")

    def should_continue(state):
        last = state["messages"][-1]
        return "tools" if last.tool_calls else END

    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    return graph.compile()
```
</details>

<details>
<summary><code>backend/main.py</code> – FastAPI + SSE</summary>

```python
app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"]
)

agent_chain = create_agent_graph()

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def events():
        async for chunk in agent_chain.astream({"messages": [HumanMessage(content=req.query)]}):
            if "agent" in chunk:
                msg = chunk["agent"]["messages"][-1].content
                if msg:
                    yield f"data: {msg}\n\n"
            await asyncio.sleep(0.1)
    return EventSourceResponse(events())
```
</details>

---

## 4 · Frontend Code

Key parts of **`frontend/src/App.jsx`**

```jsx
const eventSource = new EventSource("http://localhost:8000/chat/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query }),
});
eventSource.onmessage = (e) => updateBot(e.data);
```

Basic styling lives in **`frontend/src/App.css`**.

---

## 5 · Run 🚀

```bash
# terminal 1
cd backend && uvicorn main:app --reload

# terminal 2
cd frontend && npm run dev
```

Visit **http://localhost:5173** and ask:

```text
• How many active contracts do we have?
• Are there contracts with "Modus Media International"?
• Find contracts effective after 2018‑01‑01
• Count contracts by type
```

---

## 🛣️ Next Steps

* **Ingestion pipeline** – parse raw PDFs and populate your own graph.  
* **Clause‑level search** – index clauses as nodes (`:Clause`).  
* **Tooling upgrades** – fuzzy party matching, OR filters, schema‑guided prompts.  
* **Evaluation harness** – integrate the article’s benchmark for automated regression tests.  
* **Containerization** – wrap backend & db in Docker Compose for prod deploy.

---

## License

MIT © 2025
