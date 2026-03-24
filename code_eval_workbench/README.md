# Code Eval Workbench 🔬

A production-grade evaluation harness for LLM-powered code bug-fixing agents. Runs bug-fix tasks through any Anthropic-compatible model and scores the outputs using a multi-dimensional scorer system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **Multi-scorer evaluation** — 4 independent scorers (LLM judge, pytest, Levenshtein, composite) give a complete picture of fix quality
- **Dual backend** — works with Claude or MiniMax M2.7 via environment variable swap, no code changes
- **Rich CLI** — filter by category/difficulty, skip scorers for fast iteration, CI/CD threshold gate
- **Streamlit dashboard** — live evaluation progress, per-example diffs, score analytics, dataset studio, run history
- **Extensible dataset** — 10 curated examples; generate unlimited more with the built-in Claude-powered generator
- **GitHub Actions CI** — blocks PRs when composite score drops below threshold

---

## Quick Start

```bash
git clone <repo-url>
cd code_eval_workbench

./setup.sh          # installs deps with uv, creates .env from .env.example
$EDITOR .env        # add your ANTHROPIC_API_KEY

./run.sh            # launch Streamlit UI
# or
./run.sh cli        # run CLI evaluation
```

---

## Architecture

```
Input → Task → Scoring

dataset.py    Bug-fix examples: buggy_code + bug_description → reference_output + test_code
task.py       LLM task executor (streams response, adaptive thinking)
scorer.py     4 scorers: LLM-judge, pytest, Levenshtein, composite
run_eval.py   CLI runner with threshold gate
app.py        Streamlit dashboard (Evaluation, Analysis, Dataset Studio, History)
utils.py      Backend config, Pydantic models, code extraction, results persistence
```

**Backend resolution**: `utils.get_model_config()` auto-detects Claude or MiniMax from `ANTHROPIC_BASE_URL` in `.env`. Model config is cached at import time.

---

## CLI Reference

```bash
# Full evaluation — all examples, all scorers
python run_eval.py

# Filter examples
python run_eval.py --category arithmetic          # one or more categories
python run_eval.py --difficulty easy              # easy / medium / hard
python run_eval.py --ids bug_001 bug_002          # specific IDs

# Fast mode — skip scorers
python run_eval.py --no-llm      # skip LLM-as-judge
python run_eval.py --no-prog     # skip programmatic (pytest)
python run_eval.py --no-lev      # skip Levenshtein

# Export and gate
python run_eval.py --output results.json
python run_eval.py --threshold 0.70   # exit 1 if composite < threshold
python run_eval.py --verbose           # show LLM output preview
```

---

## Scoring System

| Scorer | Weight | What it measures |
|--------|--------|-----------------|
| **LLM-as-judge** | 50% | Claude grades correctness (40%), code quality (30%), explanation clarity (30%) |
| **Programmatic** | 30% | Extracts fixed code, runs embedded pytest — returns test pass rate |
| **Levenshtein** | 20% | Character-level similarity to reference fix via `difflib.SequenceMatcher` |
| **Composite** | — | Weighted average of enabled scorers, renormalized to weight sum |

All scorers return floats in `[0.0, 1.0]`. The composite is the primary gate metric.

---

## Backend Configuration

The SDK routes to the endpoint set in `ANTHROPIC_BASE_URL`. Swap backends with zero code changes.

**Claude (default)**
```env
ANTHROPIC_API_KEY=sk-ant-...
```

**MiniMax M2.7**
```env
ANTHROPIC_API_KEY=<minimax-key>
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
# Optional overrides:
# MODEL_OVERRIDE=MiniMax-M2.7
# MINIMAX_USE_HIGHSPEED=true      # use MiniMax-M2.7-highspeed
```

MiniMax uses `budget_tokens` thinking (fixed-budget); Claude uses `adaptive`. Both are configured automatically.

---

## Dataset

10 curated Python bug-fix examples across 7 categories:

| ID | Category | Difficulty |
|----|----------|------------|
| bug_001 | arithmetic | easy |
| bug_002 | off-by-one | easy |
| bug_003 | type-error | easy |
| bug_004 | logic | medium |
| bug_005 | python-gotcha | medium |
| bug_006 | arithmetic | easy |
| bug_007 | string-handling | easy |
| bug_008 | recursion | medium |
| bug_009 | error-handling | medium |
| bug_010 | list-comprehension | medium |

Each entry has `input` (buggy_code + bug_description), `reference_output`, and `test_code` (pytest assertions).

### Generating more examples

```python
from dataset import generate_examples

new = generate_examples(n=5, category="recursion", difficulty="hard")
```

Or via the **Dataset Studio** tab in the Streamlit UI — browse curated examples, generate new ones with Claude, and they're immediately included in evaluations.

---

## Web Dashboard

Four tabs:

- **Evaluation** — live progress bar, per-example expandable diffs (buggy vs fixed), score cards, pass/fail gate against threshold
- **Analysis** — score distribution histogram, average by category, scorer comparison per example, breakdown by difficulty
- **Dataset Studio** — browse all curated examples; generate and manage synthetic examples
- **History** — run trend chart, load and download any past run

---

## CI/CD Integration

The included GitHub Actions workflow (`.github/workflows/evals.yml`) runs on every PR to `main`/`master` that touches `code_eval_workbench/**`.

```yaml
# Trigger manually with custom threshold
on:
  workflow_dispatch:
    inputs:
      threshold:
        description: "Minimum composite score (0.0–1.0)"
        default: "0.70"
```

The workflow posts a score summary as a PR comment and fails the check if the composite drops below the threshold.

---

## Project Structure

```
code_eval_workbench/
├── app.py              Streamlit web dashboard
├── dataset.py          Bug-fix examples + Claude-powered generator
├── run_eval.py        CLI runner
├── scorer.py           4 scorers + composite
├── task.py             LLM bug-fixing executor
├── utils.py           Backend config, models, helpers
├── setup.sh           Dependency setup (uv sync)
├── run.sh             UI / CLI launcher
├── verify.sh          Test runner (uv run pytest)
├── pyproject.toml     Dependencies (uv-managed)
├── requirements.txt   Dependencies (reference)
├── .env.example       Template — copy to .env
└── tests/
    ├── conftest.py     Env setup + LLM judge mock
    ├── test_utils.py   Code extraction, formatting, model validation
    ├── test_dataset.py Filter logic, schema validation
    └── test_scorer.py  Levenshtein, programmatic, composite
```

---

## Extending the Framework

**Add a new scorer**: implement a function `score(output, input_dict, reference, test_code) -> float` in `scorer.py` and include it in the composite weight map.

**Add a dataset example**: append to the `DATASET` list in `dataset.py` with the schema:
```python
{
    "id": "bug_XXX",
    "category": "<category>",
    "difficulty": "easy|medium|hard",
    "input": {"buggy_code": "...", "bug_description": "..."},
    "reference_output": "...",
    "test_code": "def test_...(): ..."
}
```

**Backend**: `get_model_config()` in `utils.py` is the single place that resolves the SDK client, model name, thinking params, and max tokens.

---

## License

MIT License — see [LICENSE](LICENSE) for full text.
