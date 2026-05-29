# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Streamlit evaluation console for tutorial agents. The main UI entrypoint is `app.py`. Core code lives in `agent_eval/`:

- `config.py`, `models.py`: dataclass-based runtime configuration and result models.
- `dataset.py`: built-in tutorial eval cases.
- `tools.py`, `agent.py`: tool registry and tutorial agent behavior.
- `scoring.py`, `runner.py`: case scoring and eval orchestration.
- `storage.py`, `reporting.py`: SQLite persistence and JSON/CSV exports.

There is currently no committed `tests/` directory. Runtime data such as `eval_runs.db` and export files should be treated as local artifacts, not source.

## Build, Test, and Development Commands

Create an isolated environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the app locally:

```bash
streamlit run app.py
```

Run a syntax/import sanity check:

```bash
python3 -m compileall app.py agent_eval
```

If tests are added, prefer a standard `pytest` workflow and document any new command in `README.md`.

## Coding Style & Naming Conventions

Use Python 3 style with 4-space indentation, clear type hints, and small functions. Follow the existing dataclass pattern with `@dataclass(slots=True)` for structured records. Module names are lowercase with underscores; classes use `PascalCase`; functions, variables, and case IDs use `snake_case`. Keep UI logic in `app.py` and reusable evaluation logic inside `agent_eval/`.

## Testing Guidelines

Add tests under `tests/` with filenames like `test_scoring.py` or `test_runner.py`. Focus coverage on deterministic behavior: dataset loading, tool calls, scoring thresholds, repository persistence, and export formatting. Use temporary directories or in-memory SQLite paths where possible so tests do not create or depend on `eval_runs.db`.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `Add Memory Bridge prototype` and `Add live voice claims server...`. Keep commit subjects concise and action-oriented.

For pull requests, include a brief description, testing performed, and any UI-impact notes. Link related issues when available. Include screenshots or short recordings for visible Streamlit changes, especially layout or workflow updates.

## Security & Configuration Tips

Do not commit local databases, virtual environments, exported run results, or secrets. Keep tool execution constrained to `TOOL_REGISTRY`; avoid expanding `calculator` behavior without reviewing safety implications.
