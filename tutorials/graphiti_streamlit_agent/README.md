# Graphiti + LangGraph Streamlit Demo

A minimal Streamlit app that wires a simple LangGraph agent to Graphiti (Zep) for temporally-aware memory. Use it to:
- Connect to Neo4j/FalkorDB via Graphiti
- Ingest episodes (text/message/JSON)
- Search entities and relationships
- Chat with a minimal agent that retrieves from the temporal knowledge graph before responding

## Quickstart

1) Create a `.env` (or set env vars):

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

2) Install deps (ideally in a fresh venv):

```bash
pip install -r requirements.txt
```

3) Run with Docker + bootstrap (recommended):

```bash
./scripts/dev_bootstrap.sh
```

This brings up Neo4j via Docker, creates a venv, installs requirements, and launches Streamlit.

Alternatively, run Streamlit directly (ensure Neo4j is running locally first):

```bash
streamlit run app.py
```

4) In the app:
- Confirm or override connection settings in the sidebar
- Click Connect
- Optionally seed demo data
- Ingest your own episodes
- Query nodes/edges
- Chat with the agent

## Notes
- The agent uses LangGraph to orchestrate a simple Retrieve -> Generate workflow.
- If `langchain-openai` isn’t installed or `OPENAI_API_KEY` is missing, the app will fall back to a lightweight deterministic responder that summarizes retrieved memory.
- Graphiti APIs may vary between versions; if something doesn’t run, check the version you installed and adjust imports/signatures.

## Structure
- `app.py`: Streamlit UI + Graphiti integration + LangGraph agent
- `seed_data.py`: Optional seeding of a few demo episodes
- `requirements.txt`: Dependencies (Streamlit, Graphiti, LangGraph, LangChain)
- `.env.example`: Example environment variables

Enjoy experimenting!
