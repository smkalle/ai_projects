# 🚀 LangConnect + Open Agent Platform: Your End-to-End RAG Stack

### From `docker compose up` to Searchable Docs & AI-Powered Agent Workflows
---

## ✨ Why Choose This Stack?

**Unlock the power of Retrieval-Augmented Generation (RAG) with an intuitive, GUI-driven experience!**

Tired of complicated command-line tools for vector search and document retrieval? **LangConnect**, brought to you by LangChainAI, combines a modern Streamlit dashboard with a blazing-fast FastAPI backend. Process your docs, search with semantic/keyword/hybrid modes, and manage access securely using Supabase JWT—all from your browser.

With real-time document ingestion, flexible vector search powered by PostgreSQL + pgvector, and seamless agent integration, this stack puts the latest RAG techniques at your fingertips. Whether you're a developer, data scientist, or AI tinkerer, you'll be up and running in minutes.

---

## 🧩 Stack Overview

| Piece                         | What You Get                                                                                   | Tech Stack                           |
|-------------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------|
| **LangConnect**               | Chunk, embed & store docs with CRUD + multi-mode search APIs (FastAPI + pgvector)             | Python 3.11, LangChain, pgvector     |
| **Open Agent Platform (OAP)** | Next.js GUI for doc upload, hybrid/semantic queries, and LangGraph agent workflows            | TypeScript, Next.js, Supabase Auth   |
| **oap-langgraph-tools-agent** | Drop-in LangGraph agent pre-wired with LangConnect search—perfect demo of agent-RAG loop      | LangGraph CLI, FastAPI               |

---

## 1️⃣ Prerequisites

- **Docker + Docker Compose**
- **Python 3.11+** (optional, for LangConnect contributions)
- **Node.js ≥ 20** and **Yarn** (for OAP web app)
- A free **Supabase** project (for JWT authentication)

---

## 2️⃣ Clone the Repos

```bash
# Pick a workspace folder
git clone https://github.com/langchain-ai/langconnect.git
git clone https://github.com/langchain-ai/open-agent-platform.git
git clone https://github.com/langchain-ai/oap-langgraph-tools-agent.git

---

## 3. Spin up LangConnect (RAG API)

```bash
cd langconnect
# fire up Postgres + pgvector and the API
docker-compose up -d
```

What happens:

* **postgres:15** container with `pgvector` extension  
* **langconnect-api** built from `Dockerfile`, served on **:8080**

Verify:

* Swagger docs → <http://localhost:8080/docs>  
* Health check → <http://localhost:8080/health>  

_Default DB creds live in `docker-compose.yml`; override via `.env` if needed._

---

## 4. Prep Supabase Auth

1. Create a project at <https://supabase.com>.  
2. Copy **Project URL** and **Anon Key**.  
3. In `open-agent-platform/apps/web/` add a file called `.env.local`:

```dotenv
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...
# Optional: hide Google login button
# NEXT_PUBLIC_GOOGLE_AUTH_DISABLED=true
```

---

## 5. Configure Open Agent Platform (frontend)

```bash
cd ../open-agent-platform/apps/web
yarn install            # install deps
```

### Connect to LangConnect

```dotenv
# in the same .env.local
NEXT_PUBLIC_RAG_API_URL=http://localhost:8080
```
This tells OAP which RAG server backs the “Collections” tab.

### (Optional) point to your own LangGraph deployment  
OAP expects a JSON array of deployments in `NEXT_PUBLIC_DEPLOYMENTS`:

```dotenv
NEXT_PUBLIC_DEPLOYMENTS=[
  {
    "id":"bf63dc89-1de7-4a65-8336-af9ecda479d6",
    "deploymentUrl":"http://localhost:2024",
    "tenantId":"42d732b3-1324-4226-9fe9-513044dceb58",
    "name":"Local LangGraph",
    "isDefault":true,
    "defaultGraphId":"agent"
  }
]
```

---

## 6. Run the LangGraph tools agent (local)

```bash
cd ../../oap-langgraph-tools-agent
# boots a tools agent on :2024
langgraph dev --no-browser
```

The agent exposes an MCP-style endpoint that OAP can invoke.

---

## 7. Launch the web app

```bash
# back in open-agent-platform/apps/web
yarn dev      # Next.js dev mode on :3000
```

Open <http://localhost:3000> → sign in with Supabase credentials.

---

## 8. Your first RAG workflow

1. **Create collection** → “my-docs”  
2. **Upload** one or more PDFs / Markdown / TXT.  
3. Try a **hybrid search**:  
   *Query*: `“explain vector search advantages”`  
4. Click **Agents** → choose the “Local LangGraph” agent → ask:  
   > “Using the docs, summarise key advantages of pgvector over FAISS.”

The agent calls LangConnect behind the scenes, streams the answer back in chat.

---

## 9. Going further

| 💡 Idea | How-to |
|---------|--------|
| **Change embedding model** | Edit `LANGCONNECT_EMBEDDING_MODEL` env var in `docker-compose.yml`. |
| **Chunking size / overlap** | Tweak `CHUNK_SIZE` & `CHUNK_OVERLAP` env vars (see `langconnect/settings.py`). |
| **Role-based access** | Enable Supabase RLS policies; pass JWT in `Authorization: Bearer <token>` on every LangConnect API call. |
| **Production deploy** | Push containers to a registry → run on Kubernetes or a single VPS; point OAP’s env vars to the public URLs. |
| **Observability** | Add Postgres `pg_stat_statements` and OpenTelemetry export in FastAPI middleware. |

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pgvector` extension missing | Enter the DB container and `CREATE EXTENSION IF NOT EXISTS pgvector;` |
| OAP shows _“unauthenticated”_ loop | Confirm `NEXT_PUBLIC_SUPABASE_URL` & `ANON_KEY`, check browser console for 401. |
| Agent list empty | Ensure `langgraph dev` is running **and** your JSON in `NEXT_PUBLIC_DEPLOYMENTS` is valid JSON (quotes!). |
| Vector search slow | Verify index: `CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);` in Postgres. |

---

## 11. Repo structure cheat-sheet

```txt
langconnect/
 ├─ langconnect/          # FastAPI app
 │   ├─ api/              # routers
 │   ├─ db/               # SQLModel + pgvector helpers
 │   └─ embeddings/       # model abstraction
 └─ docker-compose.yml    # Postgres + API

open-agent-platform/
 └─ apps/web/             # Next.js UI
     ├─ src/              # pages, components
     └─ public/           # static assets

oap-langgraph-tools-agent/
 ├─ graph/                # LangGraph definitions
 └─ tool_wrappers/        # LangConnect search tool
```

---

## 12. License

Both LangConnect and the Open Agent Platform are MIT-licensed—fork away!

---

### Happy vector-hacking 🚀
