# AGENTS.md — insurance_workflow

## What this folder is

Design and planning docs only. **No code exists here yet.** The implementation target is `demos/insurance_claims.py` in the parent `demo-gemini-python` app, plus a new FastAPI backend and React frontend described in the specs.

## Files and what they govern

| File | Role |
|---|---|
| `insurance-flow-spec.md` | Authoritative pipeline spec: 7-step flow, Pydantic schemas, deterministic routing rules, `_parse_response()` contract, test coverage expectations |
| `technical-spec.md` | Full system architecture: API endpoints, data models, tech stack, env vars, production hardening checklist |
| `iterative-plan.md` | 4-iteration delivery plan with sign-off gates, test case IDs, and dependency map — this is the build order |
| `insflowdocumenthandling.md` | Tutorial/context doc for the upstream multimodal RAG demo (Shubham Saboo's repo). Background only; not an implementation spec. |

## Critical implementation rules (from specs)

**SDK**: Always `from google import genai`. Never `google-cloud-aiplatform`. This is a hard rule from the parent repo.

**All LLM steps** must use `response_mime_type="application/json"` and pass a schema from `Model.model_json_schema()`. No exceptions — tests assert this.

**`_parse_response()`** must normalize in this exact fallback order:
1. `response.parsed.model_dump()` if parsed is a Pydantic object
2. `response.parsed` if already a dict
3. `json.loads(response.text)`
4. `{"raw": response.text}` if JSON parsing fails

**Routing priority order** (deterministic, not LLM):
1. `safety_concerns=true` → `emergency_escalation` | Emergency Response | priority 100
2. `siu_referral_required=true` → `special_investigation` | SIU | priority 90
3. `has_all_fields=false` → `needs_documents` | Customer Service | priority 30
4. `escalation_type` exists and != `ready_for_adjuster` → that value | Claims Processing | priority 70
5. default → `ready_for_adjuster` | Claims Processing | priority 50

**Single retrieval pass**: Coverage step (Step 4) must do exactly one RAG call per `/claims` invocation. Same evidence packet feeds both the ADK agent and the UI citations.

## Build order (do not skip iterations)

Iterations have explicit sign-off gates — no iteration starts until the previous gate closes.

- **Iteration 1** (13 pts): FastAPI skeleton, Steps 1–3 + Step 6 partial, plain HTML form. Freezes `ClaimNarrative`, `ClaimClassification`, `_parse_response()`, and `/claims` API contract.
- **Iteration 2** (21 pts): Step 4 Coverage (static policy text), React + Vite frontend replacing HTML.
- **Iteration 3** (34 pts): Step 5 FraudSignals, full 5-branch routing, `POST /sources` RAG ingestion (Gemini File API + Embedding 2), coverage grounded in RAG, citations in response.
- **Iteration 4** (21 pts): Step 7 DocumentChecklist, `GET /space` PCA endpoint, Three.js 3D embedding viz, ADK agent trace surfaced.

## API endpoints (target)

| Method | Path | Description |
|---|---|---|
| `POST` | `/sources` | Ingest document/URL/text into RAG store |
| `GET` | `/space` | PCA-projected 3D coordinates for all indexed sources |
| `POST` | `/ask` | RAG retrieval + ADK agent synthesis + citations |
| `POST` | `/claims` | Full 7-step insurance pipeline |
| `GET` | `/health` | Confirms Gemini Embedding 2 + ADK availability |

## Dev ports

- Backend: `http://localhost:8897`
- Frontend: `http://localhost:5177` (run with `npm run dev -- --port 5177`)
- If backend is on a non-default host: `VITE_API_URL=http://localhost:8897 npm run dev -- --port 5177`

## Environment variables

| Variable | When needed |
|---|---|
| `GOOGLE_API_KEY` | Dev — Gemini API direct mode (backend) |
| `ALLOW_PRIVATE_URLS=true` | Dev — allow localhost/private URLs for source ingestion |
| `GOOGLE_GENAI_USE_VERTEXAI=true` | Prod — switch to Vertex AI endpoint |
| `GOOGLE_CLOUD_PROJECT` | Prod — required with Vertex AI mode |
| `GOOGLE_CLOUD_LOCATION` | Prod — region (default: `global`) |
| `PORT` | Cloud Run — auto-set (default: `8080`) |

## Key backend source files (once implemented)

- `backend/server.py` — FastAPI endpoints
- `backend/rag_store.py` — MultimodalRagStore, embedding logic, PCA projection
- `backend/agentic_rag_agent/agent.py` — ADK agent (SOURCE_INGESTOR → RETRIEVAL_TOOL → ANSWER_SYNTHESIZER)
- `demos/insurance_claims.py` — 7-step claims pipeline

## Tech stack

- LLM + Embeddings: `google-genai`, model `gemini-3.1-flash-preview`, Gemini Embedding 2
- Agent orchestration: `google-adk`
- Backend: FastAPI + Uvicorn
- Frontend: React + Vite + Three.js
- Schemas: Pydantic v2 (`model_json_schema()`, `model_dump()`)
- Vector store: in-memory `MultimodalRagStore` for dev; pgvector/Pinecone for production

