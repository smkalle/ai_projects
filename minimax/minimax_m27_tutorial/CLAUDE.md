# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a tutorial suite for the **MiniMax M2.7** model — an Anthropic-compatible API. The repository demonstrates 8 progressive modules covering text generation, streaming, multi-turn chat, tool use, extended thinking, system prompting, cost tracking, and a ReAct agent loop. It is not a production application; it is a learning/reference implementation.

## Commands

### Setup
```bash
./setup.sh                              # interactive first-run setup
./setup.sh --key YOUR_API_KEY           # non-interactive with API key
./setup.sh --endpoint cn               # use China endpoint
./setup.sh --highspeed                  # enable highspeed model variant
```

### Running Modules
```bash
python run_all.py                       # interactive module picker
python run_all.py --all                 # run all 8 modules in sequence
python run_all.py --module 04           # run a specific module by ID
python run_all.py --list                # print module list and exit
```

### Individual modules can also be run directly:
```bash
python modules/01_hello.py
```

## Architecture

```
config.py          — Model IDs, endpoints, pricing constants, MODULES registry
utils.py           — Shared utilities: load_env(), make_client(), log(), report_usage(), print_blocks()
run_all.py         — Dynamic module loader (importlib), interactive CLI
modules/
  01_hello.py       — Basic text generation, single-turn
  02_streaming.py   — Streaming responses with TTFT measurement
  03_multi_turn.py  — Multi-turn conversation, message history
  04_tool_use.py    — Function calling (calculator + weather tools)
  05_thinking.py    — Extended thinking, thinking budget
  06_system_prompt.py — Structured prompts, XML tags, few-shot
  07_cost_tracker.py — CostLedger class, budget guards, cache savings
  08_agent_loop.py  — ReAct agent loop with scratchpad memory
minimax-m27-tutorial-app.html — Interactive frontend (standalone, hits Anthropic API directly)
.env               — API credentials (gitignored)
```

## Key Patterns

- **API Client**: Uses `anthropic.Anthropic` SDK with `base_url` pointing to MiniMax endpoints (`https://api.minimax.io/anthropic` or `https://api.minimaxi.com/anthropic`)
- **Dynamic module loading**: `run_all.py` uses `importlib.util.spec_from_file_location` + `exec_module` to load modules without them being installed packages
- **Tool loop pattern**: Tool calls are detected via `block.type == "tool_use"`, dispatched to local implementations, and results are appended as `tool_result` blocks before the next `messages.create()` call
- **Thinking blocks**: Module 05 shows that `response.content` may contain `thinking` blocks separate from `text` blocks — both must be preserved in conversation history
- **Cost tracking**: Uses `usage.input_tokens`, `usage.output_tokens`, and `cache_read_input_tokens` from the Anthropic SDK usage object

## Environment Variables

| Variable | Description |
|-----------|-------------|
| `ANTHROPIC_API_KEY` | MiniMax API key |
| `ANTHROPIC_BASE_URL` | Endpoint URL (defaults to global) |
| `MINIMAX_USE_HIGHSPEED` | `true` to use MiniMax-M2.7-highspeed |

## MiniMax M2.7 Model Specs

- Context window: 204,800 tokens / Max output: 131,072 tokens
- Pricing: $0.30/1M input tokens, $1.20/1M output tokens
- Supports streaming, tool use, extended thinking natively
