# AInsurance OSS

AInsurance is an AI-first insurance claims triage demo with a FastAPI backend and React frontend.

It supports:

- narrative-based claim extraction/classification
- deterministic routing
- coverage reasoning grounded by retrieved sources
- source ingestion (`text`, `url`, and single-file uploads)
- image damage analysis with Gemini vision
- citations and debug trace payloads for auditability

## Tech Stack

- Backend: FastAPI, Pydantic v2, `google-genai`
- Frontend: React + Vite
- Retrieval store: in-memory (developer mode)

## Quick Start

1. Copy env template and set your API key:

```bash
cp .env.example .env
```

2. Install backend dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

4. Run both services:

```bash
./run.sh
```

- Backend: `http://localhost:8897`
- Frontend: `http://localhost:5177`

## Core Endpoints

- `GET /health` – basic service health
- `POST /sources` – ingest source text/url/file for retrieval grounding
- `POST /claims` – end-to-end claims pipeline with coverage, fraud signals, citations, and trace

## Notes on Quotas

Gemini free-tier quotas can return `429 RESOURCE_EXHAUSTED` during testing. The backend includes retry/fallback behavior, but sustained quota exhaustion will still block external integration paths.

## Security

- Never commit real API keys.
- Keep `.env` local only.
- Use `.env.example` as the shareable template.

## Repository Layout

- `backend/` – FastAPI server, pipeline, in-memory RAG store, tests
- `frontend/` – React app and UI assets
- `iteration*-*.md` – planning and sign-off artifacts

## License

MIT. See `LICENSE`.
