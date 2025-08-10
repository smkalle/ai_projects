# Rare Disease Drug Repurposing AI

🧬 **AI-Powered Drug Repurposing for Rare Diseases**

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

## Architecture

```
Frontend (Streamlit) → Backend (FastAPI) → AI Agents → Databases
     ↓                      ↓                ↓           ↓
  User Interface      REST API         LangChain    Vector DB
                                      Coordinator   Knowledge Graph
```

For detailed documentation, see the `docs/` directory.

## Developer Notes

- Package management: use `uv` only (no pip). The project defines dependencies in `pyproject.toml` and a dev toolchain under `[tool.uv]`.
- Common commands:
  - `uv sync --dev` — create/update the `.venv` and install deps
  - `uv run pytest -q` — run tests
  - `uv run black .` — format code
  - `uv run flake8` — lint
  - `uv run mypy src` — type-check

## License

MIT License - see LICENSE file for details.
