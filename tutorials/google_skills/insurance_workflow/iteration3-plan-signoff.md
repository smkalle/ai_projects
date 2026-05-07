# Iteration 3 Plan and Sign-Off Checklist

Date: 2026-05-07

## Objective

Deliver Iteration 3 from the approved roadmap:
- Step 5 FraudSignals
- Full 5-branch deterministic routing
- `POST /sources` ingestion (Gemini File API + Embedding 2)
- Coverage grounded in a single retrieval pass per `/claims`
- Citations returned to UI

## Scope (Must Deliver)

1. Pipeline
- Add FraudSignals schema + LLM step.
- Activate routing priority branches:
  - emergency escalation
  - SIU referral
  - needs documents
  - escalation type
  - default ready for adjuster

2. RAG / Retrieval
- Implement in-memory multimodal store for docs.
- Add `POST /sources` endpoint to ingest text/url/file.
- Enforce one retrieval pass in Step 4 per `/claims` call.

3. API
- Extend `/claims` response with:
  - fraud signals
  - citations/evidence packet references

4. Frontend
- Add source ingestion UI.
- Show citations supporting coverage decision.

## Out of Scope

- Iteration 4 document checklist step
- 3D embedding visualization (`GET /space` UX)

## Execution Checklist (Maker/Checker)

| # | Deliverable | Maker | Checker | Evidence | Status |
|---|---|---|---|---|---|
| 1 | FraudSignals schema + generation | AI Agent | Engineering Lead | `backend/schemas.py`, `backend/pipeline.py` | Completed |
| 2 | Full routing branch activation | AI Agent | Engineering Lead | `backend/server.py` (passes fraud_signals to `_routing_decision`) | Completed |
| 3 | `/sources` endpoint implemented | AI Agent | Engineering Lead | `backend/server.py`, `backend/rag_store.py`, `test_sources_endpoint_text_ingest` | Completed (text+url) |
| 4 | Single retrieval pass enforced in `/claims` | AI Agent | Engineering Lead | `backend/server.py` retrieval section (single `RAG_STORE.retrieve` call) | Completed |
| 5 | Coverage grounded by retrieved policy chunks | AI Agent | Engineering Lead | `run_coverage(... policy_context=...)` wiring in `backend/server.py` | Completed |
| 6 | Citations included in backend response | AI Agent | Engineering Lead | `ClaimsResponse.citations`, `/claims` response payload | Completed |
| 7 | Frontend source ingestion controls | AI Agent | Engineering Lead | `frontend/src/App.jsx` Source Ingestion panel | Completed |
| 8 | Frontend citations section | AI Agent | Engineering Lead | `frontend/src/App.jsx` Citations rendering | Completed |
| 9 | T3 regression suite green (plus T1/T2) | AI Agent | Engineering Lead | `pytest -m "not integration"` = 19 passed; integration smoke passed | Partial |
| 10 | Claims Ops review on fraud/safety routing | N/A | Claims Ops Lead | Manual review pending | Pending |

## Execution Results Snapshot

- Backend compile: pass (`python3 -m py_compile backend/server.py backend/pipeline.py backend/rag_store.py backend/schemas.py`)
- Backend non-integration tests: pass (`19 passed, 7 deselected`)
- Integration smoke: pass (`test_coverage_real_covered_scenario`)
- Frontend build: pass (`npm run build`)
- Debug mode default: enabled (`DEBUG` defaults to `1` in `backend/server.py`)
- Frontend always-on Debug & Progress card: implemented (`frontend/src/App.jsx`)

## Gaps vs Original Iteration 3 Spec

- File ingestion route for `/sources` is not implemented yet (text + URL only).
- Retrieval currently uses deterministic lexical scoring in-memory and does not yet call Gemini Embedding 2.
- Full T3.1-T3.10 automated matrix and Claims Ops sign-off are still pending.

## Proposed Test Matrix

- T3.1 Fraud high-risk -> SIU route priority 90
- T3.2 Safety concern -> emergency route priority 100
- T3.3 Missing fields still forces needs_documents when no higher branch
- T3.4 Escalation type branch still honored
- T3.5 Default branch unchanged
- T3.6 Source ingestion accepts text
- T3.7 Source ingestion accepts URL (dev with allow private toggle)
- T3.8 `/claims` returns citations from retrieval evidence
- T3.9 Retrieval called exactly once per `/claims` execution
- T3.10 T1+T2 regressions remain passing

## Sign-Off Gate

Required for GO:
- Engineering Lead: T3.1–T3.10 pass or explicitly blocked with mitigation
- Claims Ops Lead: Fraud/safety routing quality accepted on representative claims
- Product/Platform: Citation output is understandable in UI

Decision:
- NO-GO (pending remaining scope and sign-offs)
