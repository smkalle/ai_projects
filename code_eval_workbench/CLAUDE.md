# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Code Eval Workbench evaluates LLM bug-fixing quality via a 3-part pattern: Input → Task → Scoring. It runs bug-fix tasks through any Anthropic-compatible model and scores outputs with 4 independent scorers.

## Architecture

```
dataset.py   — Bug-fix examples (input + reference_output + test_code)
task.py      — LLM task executor (calls the model to fix bugs)
scorer.py    — 4 scorers: LLM-judge, programmatic (pytest), Levenshtein, composite
run_eval.py  — CLI runner with threshold gate
app.py       — Streamlit web dashboard (4 tabs: Evaluation, Analysis, Dataset Studio, History)
utils.py     — Model config (Claude or MiniMax), Pydantic result models, helpers
```

**Backend resolution**: `utils.get_model_config()` detects the active backend from environment variables. Default is `claude-opus-4-6` + adaptive thinking. Set `ANTHROPIC_BASE_URL` to a MiniMax endpoint to switch. Model config is cached at import time in `task.py`, `scorer.py`, and `dataset.py` — changing `.env` requires restarting.

## Commands

```bash
./setup.sh                           # Install deps with uv, create .env from .env.example
./run.sh                             # Launch Streamlit UI
./run.sh cli                         # Run CLI evaluation
./run.sh cli --threshold 0.70        # CI/CD gate
./verify.sh                          # Run tests (uv run pytest)
```

## Key Implementation Notes

- **Code extraction**: `utils.extract_code_block()` parses markdown-fenced code blocks from LLM output. The task model must respond in the format described in `task.py`'s `SYSTEM_PROMPT` (```python + Explanation: line).
- **Programmatic scorer** writes combined (fixed_code + test_code) to a temp file and runs `pytest -q`. Test functions must call the function defined in the buggy code.
- **Results persistence**: Run summaries auto-save to `results/run_<timestamp>.json`. `utils.load_all_runs()` returns runs sorted newest-first.
- **LLM judge mock in tests**: `conftest.py` patches `scorer.llm_judge_score` to return `(0.85, "Mocked reasoning")` so composite_score integration tests run without an API key.
- **GitHub Actions**: `.github/workflows/evals.yml` blocks PRs when avg composite < 0.70. Triggers on changes to `code_eval_workbench/**`.

## Backend Configuration

```env
# Claude (default)
ANTHROPIC_API_KEY=sk-ant-...

# MiniMax M2.7
ANTHROPIC_API_KEY=<minimax-key>
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
# MODEL_OVERRIDE=MiniMax-M2.7
# MINIMAX_USE_HIGHSPEED=true
```

MiniMax uses `budget_tokens` thinking; Claude uses `adaptive`. Both are configured automatically via `get_model_config()`.
