# Bertelsmann‑Style Multi‑Agent Content Search with LangGraph (A2A Edition)

Production‑grade, hands‑on tutorial and reference project for building a decentralized, agent‑to‑agent (A2A) content search system across Books, TV, and News.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env  # add your keys
python app.py
```

Try queries:
- What documentaries exist on renewable energy?
- Find books on renewable energy and related news articles


---

## Run as a service + UI

**Backend (FastAPI + Uvicorn)**
```bash
uvicorn server.main:app --reload --port 8000
```

**Frontend (Streamlit)**
```bash
streamlit run streamlit_app.py
```
Open the app (usually http://localhost:8501), set Backend URL if needed.

**API**
- `GET /health` → health check
- `POST /query` with body `{ "query": "..." }` → invokes LangGraph network and returns result.

See FastAPI docs on first steps, request bodies, and CORS if customizing further.
