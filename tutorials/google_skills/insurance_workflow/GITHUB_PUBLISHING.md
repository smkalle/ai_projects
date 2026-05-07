# GitHub Publishing Pack

Use this file to populate the repository About section and first OSS release.

## Repository Description

AI-first insurance claims triage demo with FastAPI + React, policy-grounded coverage reasoning, fraud routing, and multimodal source ingestion.

## Suggested Topics

- insurance-ai
- claims-automation
- fastapi
- react
- vite
- google-genai
- multimodal
- retrieval-augmented-generation
- agentic-ai
- startup

## Website URL (optional)

Use your deployed frontend URL, or leave blank for local/demo-only repos.

## Release Title

v0.3.0 - Iteration 3: Multimodal Ingestion, Fraud Routing, and Citations

## Release Notes

### Highlights

- Added multimodal source ingestion endpoint (`POST /sources`) for text, URL, and single-file uploads.
- Added image damage analysis workflow using Gemini vision for insurance claim photos.
- Added fraud/safety signal extraction and full deterministic routing behavior.
- Added grounded coverage flow with citations surfaced in API and UI.
- Upgraded frontend UX with scenario templates, debugging telemetry, and attachment insights.

### API Changes

- `POST /sources` now supports:
  - JSON mode: `text` and `url`
  - Multipart mode: single `file` upload with metadata
- `POST /claims` now includes:
  - `fraud_signals`
  - `citations`
  - `attachment_insights`
  - debug trace payloads (enabled by default, configurable)

### Developer Experience

- Added OSS documentation pack:
  - `README.md`
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `CODE_OF_CONDUCT.md`
  - `CHANGELOG.md`
  - `LICENSE`
- Added `.env.example` and `.gitignore` for secure local setup.

### Known Limitations

- External Gemini requests can be temporarily blocked by free-tier quota (`429 RESOURCE_EXHAUSTED`).
- Retrieval store is in-memory for dev/demo workflows.

### Upgrade Notes

1. Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.
2. Install dependencies:
   - `python3 -m pip install -r requirements.txt`
   - `cd frontend && npm install`
3. Run:
   - `./run.sh`
