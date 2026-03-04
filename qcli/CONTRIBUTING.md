# Contributing to qcli

## Setup

```bash
git clone https://github.com/smkalle/qcli.git
cd qcli
uv sync            # or: pip install -e '.[dev]'
```

## Development Workflow

1. Create a branch from `main`
2. Make changes
3. Run tests and lint:
   ```bash
   pytest
   ruff check .
   ruff format .
   ```
4. Open a pull request

## Code Style

- **Formatter/Linter**: `ruff` only (no mypy, black, or flake8)
- **Type hints**: Use `from __future__ import annotations` in all modules
- **Config/state objects**: Use `dataclasses`
- **Terminal output**: Use `rich` (no bare `print` in `cli.py`)

## Testing

- **Unit tests** (`tests/`): Cover pure Python logic. Must not import or load any model.
- **Capability tests** (`scripts/test_qwen_capabilities.py`): Run against a real model. Not part of `pytest`.

Add unit tests for any new session/CLI logic. If adding engine features, add a corresponding test in `scripts/test_qwen_capabilities.py`.

## Project Structure

```
qcli/
├── session.py   # Pure data layer — no ML dependencies
├── engine.py    # Model loading and inference
└── cli.py       # CLI entry point and REPL
tests/           # Unit tests (pytest, no GPU)
scripts/         # Integration tests (real model)
notebooks/       # Colab demos
```

## Reporting Issues

Open an issue with:
- Python version and platform
- Model ID used
- Full error traceback
- Steps to reproduce
