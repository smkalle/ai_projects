# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gemma 4 CLI is an interactive chat interface for AI engineers, wrapping the Ollama REST API to expose all four Gemma 4 model sizes with multimodal input, native function calling, and session persistence. It is a **tutorial reference implementation** for the L5 Engineer tutorial series.

## Common Commands

```bash
# First-time setup (installs Python env, Ollama, pulls default e4b model)
chmod +x setup.sh run.sh
./setup.sh

# Launch chat (defaults from .env: e4b, temp 0.7, 32K ctx)
./run.sh

# Presets
./run.sh --max          # 31B + 256K context (best quality)
./run.sh --agent        # 26B MoE + function calling
./run.sh --code-mode    # e4b + SDE3 prompt + temp 0.2
./run.sh --edge         # e2b (minimum VRAM ~3.2 GB)
./run.sh --multilingual Tamil

# Override individual settings
./run.sh --model 31b --ctx 262144 --temp 0.3 --tools --log

# Dry-run to preview the Python command
./run.sh --dry-run

# Re-run setup after updating
./setup.sh --force

# Python-only (skip shell wrapper)
python gemma4_cli.py --model e4b --ctx 32768 --temp 0.7
```

## Architecture

```
gemma4_cli.py
├── OllamaClient          — Thin REST wrapper (GET /api/tags, POST /api/chat streaming, POST /api/pull)
├── ConversationManager   — Message history, token stats, save/load/export (JSON + Markdown)
├── Tool layer            — 5 built-in tools (get_weather, calculate, read_file, list_directory, get_system_info) + agentic loop (up to 8 rounds)
└── Gemma4CLI             — Rich TUI, command dispatcher, streaming chat renderer

run.sh                     — Launch orchestrator: env loading, preset expansion, Ollama lifecycle (auto-start/stop), flag-to-Python pass-through
setup.sh                   — One-time bootstrap: OS detection, venv, Ollama install, model pull, .env generation
.env                       — Auto-generated runtime config (model, temperature, ctx size, paths)
```

## Key Design Notes

- **`run.sh` is the only entry point.** It composes environment variables and CLI flags into a single `python gemma4_cli.py` invocation. Direct Python calls bypass environment loading and Ollama lifecycle management.
- **`--dry-run` always works** — it prints the exact Python command without executing anything.
- **Ollama auto-start**: `run.sh` checks if Ollama is running at `OLLAMA_HOST`; if not and `--no-start-ollama` is absent, it starts `ollama serve` in the background and waits up to `--wait-ollama` seconds.
- **Session log**: `--log` pipes the full CLI session (including streaming output) to `logs/session_<timestamp>.log`.
- **Image attachment**: Queue with `/image /path` in chat, then type your prompt — the image is base64-encoded and appended to the next user message.
- **Tool calling**: When enabled (`--tools` or `/tools`), the model can call any of the 5 built-in tools. The CLI loops up to 8 rounds per user turn to satisfy tool chains.
- **No test suite** — this is a reference tutorial, not a deployed library.
