# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

```
minimax/                          # Root — tutorial suite for MiniMax M2.7
├── CLAUDE.md                     # This file
├── minmax_tut.py                 # Standalone single-file tutorial (dotenv + basic call)
├── mmtest.py                     # Minimal test: API call with thinking/text block handling
└── minimax_m27_tutorial/         # Main project — 8 progressive tutorial modules
    ├── CLAUDE.md                 # Detailed guidance for the main project
    ├── config.py                 # Model IDs, endpoints, pricing, MODULES registry
    ├── utils.py                  # Shared utilities: load_env, make_client, log, report_usage
    ├── run_all.py                # Dynamic module runner (importlib, interactive CLI)
    ├── run.sh                    # Bash runner with richer CLI (loop, logging, dry-run)
    ├── setup.sh                  # First-run environment setup
    ├── requirements.txt
    ├── .env                      # API credentials (gitignored)
    └── modules/                  # 8 tutorial modules (01–08)
```

## Root-Level Scripts

`minmax_tut.py` — Self-contained tutorial showing environment setup, client creation, and a single `client.messages.create()` call. Run directly with `python minmax_tut.py`.

`mmtest.py` — Minimal test script demonstrating basic API call and handling of `thinking`/`text` content blocks. Run with `python mmtest.py`.

## Main Project

`minimax_m27_tutorial/` contains a complete tutorial suite (8 modules, progressive complexity). See `minimax_m27_tutorial/CLAUDE.md` for the full reference — setup commands, module descriptions, key patterns, and environment variables.

## MiniMax M2.7 Model Specs

- Context window: 204,800 tokens / Max output: 131,072 tokens
- Pricing: $0.30/1M input tokens, $1.20/1M output tokens
- Endpoints: `https://api.minimax.io/anthropic` (global) or `https://api.minimaxi.com/anthropic` (China)
- Two model variants: `MiniMax-M2.7` (standard) and `MiniMax-M2.7-highspeed`
- Supports streaming, tool use, extended thinking natively
