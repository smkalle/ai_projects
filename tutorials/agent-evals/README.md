# Agent Evals Console

Streamlit-based agent admin console with an end-to-end evaluation harness.
The repository also includes a V2 FastAPI + Vite dashboard for multi-model evaluation workflows.

## Features

- Agent controls (profile, runtime params, dataset, retries, timeout)
- Background eval execution with live step-by-step events
- SQLite-backed run history and case-level results
- Deterministic + semantic-lite scoring with rubric variants
- Tutorial and regression datasets for comparison runs
- Pluggable agent backend with local heuristic and OpenAI-compatible options
- Export run results as JSON/CSV
- V2 REST API for run orchestration, analytics, audit events, support answers, and VC-readiness readouts
- V2 Vite dashboard with batch controls, model/scenario analytics, observability matrix, case evidence, and audit trail
- API and Playwright smoke coverage for the v2 workflows

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To use the OpenAI-compatible backend, select an `openai:*` model in the sidebar and set `OPENAI_API_KEY`.
Override the chat completions endpoint with `OPENAI_CHAT_COMPLETIONS_URL` if needed.

## V2 FastAPI + Vite app

Run the API:

```bash
python3 -m uvicorn agent_eval.api:app --reload --port 8000
```

Run the Vite frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` for the V2 dashboard. It supports single scenario runs, multi-model x multi-scenario matrix runs, VC-readiness readouts, model leaderboards, and case-level evidence. The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

Current v2 behavior:

- `POST /api/vc-readout` returns a safe empty-state readiness response when no runs are selected.
- Matrix runs cover multiple models and scenarios and populate readiness, leaderboard, observability, case evidence, and audit views.
- The support panel exercises the tutorial agent and exposes tool evidence for each answer.

Build the frontend:

```bash
cd frontend
npm run build
```

Run the browser automation:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Run the full API and UI validation suite with signoff report:

```bash
./scripts/validate_v2_suite.sh
```

The suite writes `artifacts/v2-suite-signoff.md` with command results and workflow coverage.

Latest validation:

```text
python3 -m compileall app.py agent_eval
python3 -m pytest tests                 # 4 passed
npm --prefix frontend run build
npm --prefix frontend run test:e2e      # 3 passed
./scripts/validate_v2_suite.sh          # PASS
```

## GitHub hygiene

The project `.gitignore` excludes local runtime and generated files:

- Python caches and pytest cache
- `eval_runs.db`
- `artifacts/`
- `frontend/dist/`
- `frontend/node_modules/`
- `frontend/test-results/`
- `frontend/playwright-report/`

Before pushing, stage source and test files only. Regenerate `artifacts/v2-suite-signoff.md` locally with `./scripts/validate_v2_suite.sh` when a fresh validation record is needed, but do not commit generated artifacts unless a release process explicitly asks for them.

## Project layout

- `app.py` - Streamlit UI
- `agent_eval/config.py` - runtime config schema
- `agent_eval/models.py` - data models
- `agent_eval/dataset.py` - tutorial and regression eval datasets
- `agent_eval/tools.py` - tool registry for agent actions
- `agent_eval/agent.py` - tutorial agent runtime and backend interface
- `agent_eval/scoring.py` - assertions, scoring, and rubric variants
- `agent_eval/storage.py` - SQLite persistence
- `agent_eval/runner.py` - orchestrates eval runs and step events
- `agent_eval/background.py` - thread-backed background run manager
- `agent_eval/reporting.py` - export helpers
- `agent_eval/api.py` - V2 FastAPI endpoints
- `frontend/` - V2 Vite dashboard and Playwright UI smoke tests
- `scripts/validate_v2_suite.sh` - compile, API, build, and browser validation suite
- `tests/` - API workflow tests
