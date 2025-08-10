# Rare Disease Drug Repurposing AI

🧬 Accelerated Drug Repurposing for Rare Diseases

## Mission & Top Priority

Accelerated Drug Repurposing for Rare Diseases is the top priority. It is profoundly humanity‑saving: rare diseases often lack funding and timely treatment options, leading to avoidable mortality. This project focuses on rapidly identifying promising repurposing candidates among already FDA‑approved drugs and presenting transparent, fully cited evidence to help clinicians and regulators assess viability faster. With LangChain tooling, we can prototype a workflow that queries structured biomedical data, retrieves literature, generates testable hypotheses, and outputs cited, reproducible reports suitable for clinical and regulatory review.

This repository contains a production‑minded, open‑source foundation to: ingest structured/biomedical sources, run retrieval‑augmented analysis, score/rank candidates, and generate auditable reports with claim‑evidence traceability.

## Quick Start

### 1. Install uv (one-time)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync dependencies with uv
```bash
uv sync --dev
```

### 3. Start Backend
```bash
uv run python scripts/run_backend.py
```

### 4. Start Frontend (in new terminal)
```bash
uv run python scripts/run_frontend.py
```

### 5. Access the App
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Demo Mode

The system runs in demo mode by default with:
- ✅ Mock data for diseases and drugs
- ✅ Realistic AI analysis results  
- ✅ No API keys required
- ✅ Fast local processing

## Features

- 🔬 **AI-Powered Analysis**: Drug repurposing with confidence scoring
- 📚 **Citation Verification**: Every recommendation is source-verified
- 🎨 **Modern UI**: Silicon Valley-style Streamlit interface
- 🚀 **FastAPI Backend**: High-performance async API
- 🐋 **Docker Ready**: Full containerization support
- 🧪 **Testing Suite**: Comprehensive test coverage

## What We’re Building First (MVP)

- Evidence‑grounded RAG pipeline for a single rare disease query
- Candidate drug ranking with transparent scoring and contraindication flags
- Auto‑generated report: summary, rationale, and inline citations (PubMed/ClinicalTrials/etc.)
- Demonstration UI + REST API with downloadable, versioned report artifacts

## Architecture

```
Frontend (Streamlit) → Backend (FastAPI) → AI Agents → Databases
     ↓                      ↓                ↓           ↓
  User Interface      REST API         LangChain    Vector DB
                                      Coordinator   Knowledge Graph
```

For detailed documentation, see the `docs/` directory:
- `docs/product-spec.md` — Product spec and requirements
- `docs/architecture.md` — High‑level system architecture
- `docs/system-architecture-rare-disease-drug-repurposing-ai.md` — Extended architecture
- `docs/api-specification-rare-disease-drug-repurposing-ai.md` — API specification

## Developer Notes

- Package management: use `uv` only (no pip). The project defines dependencies in `pyproject.toml` and a dev toolchain under `[tool.uv]`.
- Common commands:
  - `uv sync --dev` — create/update the `.venv` and install deps
  - `uv run pytest -q` — run tests
  - `uv run black .` — format code
  - `uv run flake8` — lint
  - `uv run mypy src` — type-check

## License

MIT License — see `LICENSE` for details.

If you use this project in research or clinical contexts, ensure compliance with local regulations. Outputs are decision support only and not medical advice.
