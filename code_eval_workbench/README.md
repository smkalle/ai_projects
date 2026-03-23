# Code Eval Workbench 🔬

A production-grade evaluation harness for Claude-powered code bug-fixing agents.
Built on the **3-part eval framework**: Inputs → Task → Scoring Function.

## Architecture

```
code_eval_workbench/
├── dataset.py       # 10 curated bug-fix pairs + Claude-powered generator
├── task.py          # Claude bug-fixer (claude-opus-4-6, adaptive thinking, streaming)
├── scorer.py        # 4 scorers: LLM-judge, pytest runner, Levenshtein, composite
├── run_eval.py      # Rich CLI runner with threshold gate
├── app.py           # Streamlit web dashboard
└── utils.py         # Shared models and helpers
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run CLI evaluation
python run_eval.py

# Launch web UI
streamlit run app.py
```

## CLI Usage

```bash
python run_eval.py                          # All examples, all scorers
python run_eval.py --category arithmetic    # Filter by category
python run_eval.py --difficulty easy        # Filter by difficulty
python run_eval.py --no-llm                 # Skip LLM judge (fast)
python run_eval.py --threshold 0.70         # CI/CD gate: exit 1 if < 0.70
python run_eval.py --output results.json    # Export results
```

## Scorers

| Scorer | Weight | Description |
|--------|--------|-------------|
| LLM-as-judge | 50% | Claude grades correctness (0.4), code quality (0.3), explanation (0.3) |
| Programmatic | 30% | Extracts fixed code, runs embedded pytest tests, returns pass rate |
| Levenshtein | 20% | `difflib.SequenceMatcher` similarity vs reference (no API cost) |
| **Composite** | — | Weighted average of active scorers |

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

Generate more with Claude via the Dataset Studio tab or:
```python
from dataset import generate_examples
new = generate_examples(n=5, category="recursion", difficulty="hard")
```

## Model

- **Task model:** `claude-opus-4-6` with `thinking: {"type": "adaptive"}` + streaming
- **Judge model:** `claude-opus-4-6` with `thinking: {"type": "adaptive"}`
- **Generator model:** `claude-opus-4-6` with `thinking: {"type": "adaptive"}`

## CI/CD

The included GitHub Actions workflow blocks PRs when composite score drops below threshold:

```yaml
# .github/workflows/evals.yml
# Triggers on PR to main/master when code_eval_workbench/** changes
# Fails if avg_composite < 0.70 (configurable via workflow_dispatch input)
```

## Iteration Loop

```
Run → score 0.45
  ↓
Improve prompt in task.py (add examples, tighten format)
  ↓
Re-run → score 0.72
  ↓
Add edge cases to dataset → score 0.81
  ↓
Ship with threshold gate
```

## Web UI Features

- **Evaluation tab:** Live progress, per-example expandable diffs, score cards
- **Analysis tab:** Score distribution, category/difficulty breakdown, scorer comparison
- **Dataset Studio:** Browse curated examples, generate new ones with Claude
- **History tab:** Run trend chart, cross-run comparison, JSON export
