# Architecture Overview — Rare Disease Drug Repurposing AI

## High-Level Components

- Frontend (Streamlit): disease query, candidate review, report export
- Backend (FastAPI): REST endpoints, task orchestration, provenance store
- Agents (LangChain): planning, retrieval, hypothesis generation, citation mapping
- Retrieval: hybrid BM25 + vector search over structured + literature corpora
- Ranking: multi‑criteria scoring and reranking
- Storage: vector store, relational store for metadata/provenance, object store for reports
- Observability: tracing and metrics for each stage

## Data Flow

User → UI → REST API → Orchestrator →
  1) Retrieve structured + unstructured evidence →
  2) Generate structured hypotheses (LLM) →
  3) Score & rank →
  4) Assemble report with citations →
  5) Persist artifacts and provenance → UI download/API

## ASCII Diagram

```
[Streamlit UI]
    │
    ▼
[FastAPI]───▶[Orchestrator]
                 │
     ┌───────────┴───────────┐
     ▼                       ▼
[Hybrid Retrieval]      [LLM Generation]
  │      │                 │     │
  ▼      ▼                 ▼     ▼
[BM25] [Vector]        [Hypotheses] [Citations]
     \     /                 │
      ▼  ▼                   │
     [Rerank & Score] ◀──────┘
           │
           ▼
      [Report Builder] → [Provenance Store] → [Artifacts]
```

## Key Design Choices

- Structured outputs: pydantic schemas to constrain LLM outputs; strict validation
- Provenance first: every claim ties to citations and retrieval IDs
- Hybrid retrieval: robust to sparse biomedical language; better recall/precision
- Safety checks: contraindications and warnings surfaced alongside rationale
- Modularity: ingestion, retrieval, generation, ranking, and reporting are separable

## Deployment Notes

- Local/dev: run Streamlit + FastAPI + local vector DB
- Containerized: Dockerfiles provided; compose for multi‑service dev
- Secrets: `.env` for local; recommend vault/secret manager in prod

