# Contributing

Thanks for your interest in contributing! We welcome issues, discussions, and pull requests that improve transparency, safety, and usefulness.

## Getting Started

- Install dependencies with `uv sync --dev`
- Run tests with `uv run pytest -q`
- Lint/format with `uv run flake8` and `uv run black .`

## Pull Requests

- Open an issue first for significant changes
- Write focused commits with clear messages
- Add or update tests when changing behavior
- Document user‑facing changes in `README.md` or `docs/`

## Code Style

- Follow PEP 8, type annotate new code
- Prefer pure functions and explicit dependencies
- Validate all LLM outputs with schemas; never trust free‑form JSON

## Safety & Provenance

- Preserve citations and IDs across the pipeline
- Never introduce PHI in test data; redact where necessary
- Flag potential safety issues (DDI, contraindications) early and visibly

## Releases

- Update `CHANGELOG.md`
- Ensure version bump in `pyproject.toml` if applicable

