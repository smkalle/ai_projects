# MiniMax M2.7 Tutorial Suite

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

A progressive, hands-on tutorial suite for the **MiniMax M2.7** model — an Anthropic-compatible API with 204,800 token context, native streaming, tool use, and extended thinking.

8 modules walk you from basic text generation through to a production-ready ReAct agent loop. Every module is self-contained and runnable individually.

---

## What's Inside

8 progressive tutorial modules:

| # | Module | Key Concept |
|---|--------|------------|
| 01 | Hello World | Single-turn text generation, `content` blocks, usage metadata |
| 02 | Streaming | Real-time token streaming, TTFT measurement |
| 03 | Multi-Turn Chat | Message history, `response.content` preservation, 204K context |
| 04 | Tool Use | Function calling, `tool_use` block detection, local dispatch |
| 05 | Extended Thinking | `thinking` blocks, `budget_tokens`, interleaved reasoning |
| 06 | System Prompting | XML constraint tags, few-shot examples, structured prompts |
| 07 | Cost Tracking | `CostLedger`, cache token accounting, budget enforcement |
| 08 | Agent ReAct Loop | Full ReAct pattern, scratchpad memory, multi-tool orchestration |

---

## Prerequisites

- Python 3.10+
- A MiniMax API key — [get one at platform.minimax.io](https://platform.minimax.io)

---

## Quick Start

```bash
# 1. Enter the tutorial directory
cd minimax_m27_tutorial

# 2. First-run setup (creates venv, installs deps, writes .env)
./setup.sh --key YOUR_MINIMAX_API_KEY

# 3. Run a module
./run.sh --module 01
```

That's it. No configuration files to edit manually.

---

## Running Modules

```bash
# List all modules
./run.sh --list

# Run a specific module
./run.sh --module 04

# Run all modules in sequence
./run.sh --all

# Run a range of modules
./run.sh --all --from 03 --to 06

# Run with highspeed model variant
./run.sh --module 02 --highspeed

# Tee output to a log file
./run.sh --module 04 --log

# Verify environment without running
./run.sh --check
```

Or use the Python runner directly:

```bash
python run_all.py --list
python run_all.py --module 04
python run_all.py --all
```

---

## Model Specifications

| | |
|---|---|
| Model | `MiniMax-M2.7` or `MiniMax-M2.7-highspeed` |
| Context window | 204,800 tokens |
| Max output | 131,072 tokens |
| Input pricing | $0.30 / 1M tokens |
| Output pricing | $1.20 / 1M tokens |
| Global endpoint | `https://api.minimax.io/anthropic` |
| China endpoint | `https://api.minimaxi.com/anthropic` |

---

## Project Structure

```
minimax_m27_tutorial/
├── config.py          # Model IDs, endpoints, pricing, MODULES registry
├── utils.py           # load_env(), make_client(), log(), report_usage()
├── run_all.py         # Dynamic module loader (Python, importlib)
├── run.sh             # Bash runner with richer CLI
├── setup.sh           # First-run environment setup
├── requirements.txt
├── .env               # API credentials (gitignored)
└── modules/
    ├── 01_hello.py
    ├── 02_streaming.py
    ├── 03_multi_turn.py
    ├── 04_tool_use.py
    ├── 05_thinking.py
    ├── 06_system_prompt.py
    ├── 07_cost_tracker.py
    └── 08_agent_loop.py
```

---

## Key Patterns

**API client** — Uses `anthropic.Anthropic` SDK with `base_url` pointing to MiniMax:

```python
from utils import load_env, make_client
api_key, base_url, model = load_env()
client = make_client(api_key, base_url)
```

**Streaming** — `client.messages.stream()` as a context manager, iterate `text_stream`, call `get_final_message()` for usage stats:

```python
with client.messages.stream(model=model, ...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
message = stream.get_final_message()
```

**Tool loop** — Detect via `block.type == "tool_use"`, dispatch locally, append `tool_result` blocks:

```python
for block in response.content:
    if block.type == "tool_use":
        result = dispatch(block.name, block.input)
        history.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}]})
```

**Thinking blocks** — `response.content` may contain both `thinking` and `text` blocks. Always preserve full `response.content` in history, never just `extract_text()`:

```python
history.append({"role": "assistant", "content": response.content})  # verbatim
```

---

## License

MIT License — see [LICENSE](LICENSE) for full terms.
