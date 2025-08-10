# Product Specification — Rare Disease Drug Repurposing AI

## Summary

Top priority: accelerate drug repurposing for rare diseases by surfacing promising FDA‑approved candidates with transparent, citable evidence. The system ingests structured/biomedical sources, runs retrieval‑augmented analysis with LangChain, scores and ranks candidates, and generates auditable reports with claim‑evidence traceability to support faster clinical and regulatory assessment.

## Problem & Goals

- Problem: Rare diseases lack funding and trials; evidence is fragmented across structured databases and literature.
- Primary goal: Rapid, evidence‑grounded hypotheses for repurposing existing drugs with clear citations and risk/benefit context.
- Secondary goals: Repeatable workflows, auditability, and a pathway to clinical validation.

## Users & Use Cases

- Clinician/researcher: Query a disease, review ranked drug candidates with evidence and contraindications, export a citable report.
- Regulator/ethics reviewer: Audit provenance, confirm safety signals, and assess rationale.
- Data scientist: Extend pipelines, add sources, tune retrieval and ranking.

## Data Sources (initial targets)

- Structured: FDA Orange Book/Label, DrugBank, PubChem, RxNorm, MeSH, ClinicalTrials.gov
- Knowledge: OMIM, Orphanet, Monarch Initiative
- Literature: PubMed and related indexing

Note: Integrations may use public dumps or APIs; begin with mock/demo datasets and incrementally add connectors.

## Core Capabilities

- Retrieval‑augmented generation (RAG) over structured + unstructured sources with hybrid retrieval (BM25 + embeddings)
- Hypothesis generation with structured outputs (pydantic schema) including: mechanism, indication relevance, dosage context, contraindications, confidence
- Citation mapping: each claim links to one or more sources with passage‑level evidence
- Safety checks: drug–disease interactions, known contraindications, black‑box warnings
- Ranking: multi‑factor scoring combining relevance, evidence strength, safety risk, novelty
- Reporting: export PDF/HTML/JSON with frozen IDs and digest for auditability
- Feedback loop: thumbs up/down, rationale edits, and clinician notes feed evaluation

## Non‑Functional Requirements

- Transparency: deterministic pipelines with recorded prompts, seeds, and retrieval sets
- Observability: tracing spans for ingestion, retrieval, generation, and ranking
- Security: least‑privilege tokens, no PHI by default, safe redaction utilities
- Performance: single‑disease query end‑to‑end < 60s in demo mode
- Reliability: deterministic tests for core ranking and schema validation

## MVP Scope

- Single‑disease query UI + REST endpoint
- Ingestion of a minimal demo corpus (mock structured tables + curated abstracts)
- Vector + keyword retrieval, rerank with LLM‑assisted scoring
- Candidate generation and report export with citations

## End‑to‑End Workflow

1) Ingest & index
- Parse demo CSV/JSON for drugs, indications, warnings; chunk and embed literature
- Build vector store + BM25 index; persist document/store IDs

2) Plan & retrieve (LangChain Agent)
- Build a plan (disease → synonyms → pathways → candidate drug sets)
- Execute hybrid retrieval over structured tables + literature

3) Generate structured hypotheses
- LLM produces `DrugHypothesis` with fields: `drug_id`, `mechanism`, `rationale`, `citations[]`, `risks[]`, `confidence`

4) Score & rank
- Scoring = weighted sum of (relevance, evidence strength, safety risk, novelty)
- Re‑rank using reranker model or LLM‑as‑judge with constrained rubric

5) Report assembly
- Assemble summary + sections per candidate with inline citations
- Emit JSON + HTML/PDF; attach provenance (retrieval set, prompts, model versions)

## Data Model (draft)

- Disease: `id`, `name`, `synonyms[]`, `mesh_ids[]`
- Drug: `id`, `name`, `synonyms[]`, `fda_status`, `atc[]`, `contraindications[]`
- Evidence: `source_id`, `type`, `passage`, `score`, `url`, `citation`
- Hypothesis: `drug_id`, `mechanism`, `rationale`, `evidence_ids[]`, `risks[]`, `confidence`
- Report: `id`, `disease_id`, `generated_at`, `candidates[]`, `provenance`

## Evaluation & Metrics

- Offline: retrieval precision@k, citation accuracy, schema validity, determinism
- Human‑in‑the‑loop: clinician preference rate, usefulness score, time saved
- Safety: contraindication detection rate, harmful suggestion rate (target: ~0)

## Regulatory & Ethics Considerations

- This is decision support, not medical advice; include disclaimers
- Preserve citations and full provenance for auditability; version reports
- Track prompts, models, seeds; avoid PHI; redact if present

## Roadmap (high level)

- v0.1: MVP demo with mock data, exportable reports, tracing
- v0.2: Add real data connectors, stronger reranking, batch disease mode
- v0.3: Safety expansions (DDI, dose range checks), clinician feedback UI
- v0.4: Tuning, evaluation datasets, and continuous benchmarking

