# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

qcli is a local-first terminal chat application for running Hugging Face language models (primarily Qwen) on-device with no hosted API. Built with Python, PyTorch, and HuggingFace Transformers.

## Commands

```bash
# Install (uv preferred — lockfile exists)
uv sync

# Install with pip
pip install -e '.[dev]'       # dev deps (pytest, ruff)
pip install -e '.[quant]'     # bitsandbytes for CUDA quantization

# Run
qcli --model Qwen/Qwen3.5-2B
python -m qcli --model Qwen/Qwen3.5-2B

# Tests (unit tests only, no GPU/model needed)
pytest

# Run a single test
pytest tests/test_session.py::test_name

# Lint and format
ruff check .
ruff format .

# Integration test (downloads real model)
bash scripts/run_real_model_test.sh

# Capability tests (real model, verbose)
HF_HUB_DISABLE_XET=1 uv run python scripts/test_qwen_capabilities.py --model Qwen/Qwen2.5-0.5B-Instruct --device cpu -v
```

## Platform Notes

- On Termux/proot: `transformers<4.50` and `accelerate<1.0` are pinned due to broken native extensions (`tokenizers`, `hf_xet`)
- Set `HF_HUB_DISABLE_XET=1` when running on proot to avoid xet download errors
- Set `UV_LINK_MODE=copy` if uv hardlink fails on cross-filesystem mounts

## Architecture

Three-module design in `qcli/`:

- **`session.py`** — Pure data layer. `ChatSession` and `GenerationConfig` dataclasses, JSON save/load, slash command parsing (`parse_command()`). No model dependencies.
- **`engine.py`** — Model loading and inference. `LocalHFEngine` handles device auto-detection (CUDA→MPS→CPU), tokenizer loading, optional BitsAndBytes quantization, and streaming generation via `TextIteratorStreamer` + background `Thread`.
- **`cli.py`** — Entry point. Argparse CLI, REPL loop, slash command dispatch (`/help /clear /save /load /system /set /exit`). `main()` is the console script entry point, also used by `__main__.py`.

## Conventions

- **Dataclasses** for all config/state objects (`EngineOptions`, `GenerationConfig`, `ChatSession`)
- **`from __future__ import annotations`** in all modules
- **`ruff`** is the sole linter/formatter (no mypy, black, or flake8)
- **`rich`** for all terminal output (colored prompts, panels, markup)
- **Unit tests avoid model loading** — tests cover pure Python logic only; real model tests live in `scripts/`
- **Streaming is default** — `generate_stream()` runs inference in a background thread; `--no-stream` collects silently
