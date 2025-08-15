# Repository Guidelines

## Project Structure & Module Organization
- `src/api/`: FastAPI backend (`main.py`, routes, middleware).
- `src/mcp_agent/`: Core agent logic (`core.py`, `models.py`, `config.py`).
- `src/ui/`: Streamlit frontend (`streamlit_app.py`, `utils.py`, `components.py`).
- `tests/`: Pytest suites (`test_api.py`, `test_core.py`, `test_ui.py`).
- `scripts/`: Helper scripts (`setup.sh`, `run_dev.sh`, `deploy.sh`).
- `docs/`: Reference, tutorial, deployment guides.
- `docker/`: `Dockerfile`, `docker-compose.yml`, container configs.
- `examples/`: Minimal agents demonstrating usage.

## Build, Test, and Development Commands
```bash
# First-time setup
./scripts/setup.sh  # creates venv, installs deps, copies .env
source venv/bin/activate

# Run locally (API + UI)
./scripts/run_dev.sh
# or run separately
uvicorn src.api.main:app --reload &
streamlit run src/ui/streamlit_app.py

# Tests
pytest -q
pytest --cov=src tests/

# Docker
docker-compose up --build
```

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indentation, type hints required in new code.
- Naming: modules/files `snake_case.py`, classes `PascalCase`, functions/vars `snake_case`.
- Formatting and linting: use Black, isort, Flake8, MyPy.
```bash
black src tests && isort src tests && flake8 && mypy src
```
- Keep API schemas in `src/mcp_agent/models.py`; avoid duplicating types.

## Testing Guidelines
- Framework: Pytest (+ `pytest-asyncio` for async), `fastapi.testclient` for API.
- Location/pattern: place tests under `tests/`, name files `test_*.py`, classes `Test*`, funcs `test_*`.
- Coverage: aim for high coverage on `src/mcp_agent/core.py` and API endpoints.
- Use `unittest.mock`/`AsyncMock` to isolate external services (OpenAI, Anthropic, MCP).

## Commit & Pull Request Guidelines
- Commits: imperative mood, small, and scoped. Prefer Conventional Commits (e.g., `feat:`, `fix:`, `docs:`).
- PRs: clear description, linked issues, screenshots/GIFs for UI, and test results (include coverage command/output).
- Include updates to docs (`docs/*.md`) when changing APIs or UX; run format/lint before requesting review.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets. Populate provider keys (OpenAI/Anthropic) used by the agent.
- Local URLs: API `http://localhost:8000`, UI `http://localhost:8501` (config in `src/ui/streamlit_app.py`).
- When adding new tools/servers, register their names in agent configs and ensure they are reachable by MCP.

