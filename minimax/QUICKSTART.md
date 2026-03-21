# Quickstart — MiniMax M2.7 Tutorial Suite

A complete walkthrough from zero to a running ReAct agent. Estimated time: **15–30 minutes**.

---

## Table of Contents

1. [Get an API Key](#1-get-an-api-key)
2. [Run Setup](#2-run-setup)
3. [Your First Module](#3-your-first-module)
4. [All Modules Reference](#4-all-modules-reference)
5. [Common Tasks](#5-common-tasks)
6. [Environment Variables](#6-environment-variables)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Get an API Key

Sign up at [platform.minimax.io](https://platform.minimax.io) and create an API key. The free tier includes a generous token allowance — sufficient to work through all 8 modules.

---

## 2. Run Setup

```bash
cd minimax_m27_tutorial
./setup.sh --key YOUR_MINIMAX_API_KEY
```

This script (in order):

1. **Checks Python 3.10+** — aborts if missing
2. **Creates a virtual environment** at `.venv/` (or custom via `--venv myenv`)
3. **Installs dependencies** — `anthropic`, `python-dotenv`
4. **Writes `.env`** with your API key and endpoint
5. **Validates** — confirms packages import and key is present

### Setup Flags

| Flag | Effect |
|------|--------|
| `--key KEY` | Set API key non-interactively |
| `--endpoint cn` | Use China endpoint (`api.minimaxi.com`) |
| `--endpoint global` | Use global endpoint (default) |
| `--highspeed` | Enable `MiniMax-M2.7-highspeed` variant |
| `--venv myenv` | Custom venv directory name |
| `--skip-venv` | Use system Python |
| `--skip-install` | Skip pip install (venv already ready) |
| `--force` | Overwrite existing `.env` |
| `--dry-run` | Print actions without executing |

After setup completes, activate the venv and verify:

```bash
source .venv/bin/activate   # or: source myenv/bin/activate
./run.sh --check
```

---

## 3. Your First Module

```bash
./run.sh --module 01
```

You should see output like:

```
════════════════════════════════════════════════════
  Module 01 · Hello World — Basic Text Generation
════════════════════════════════════════════════════

[14:23:01] [ENV]     Endpoint  : https://api.minimax.io/anthropic
[14:23:01] [ENV]     API key   : abc123...xyz9
[14:23:01] [ENV]     Model     : MiniMax-M2.7
[14:23:01] [CLIENT]  Anthropic client initialised → MiniMax endpoint

─────────────────────────────── Request ───────────────────────────────

[REQUEST] model      = MiniMax-M2.7
[REQUEST] max_tokens = 512

─────────────────────────────── API Call ─────────────────────────────

[14:23:02] [RESPONSE] Success
...
```

### What just happened

`01_hello.py` calls `client.messages.create()` with a single user message, receives a `response` object, and prints:

- **Metadata** — `id`, `model`, `role`, `stop_reason`
- **Content blocks** — `text` blocks (and `thinking` blocks if enabled)
- **Usage** — input/output token counts and estimated cost

Key lesson: `response.content` is a **list of blocks**, not a plain string. Iterate it to find `text`, `thinking`, or `tool_use` blocks.

---

## 4. All Modules Reference

### Module 01 — Hello World
**File:** `modules/01_hello.py`

First API call. Establishes the core pattern:

```python
from utils import load_env, make_client, print_blocks, report_usage
api_key, base_url, model = load_env()
client = make_client(api_key, base_url)

response = client.messages.create(
    model=model,
    max_tokens=512,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello!"}]
)

print_blocks(response)
report_usage(response.usage)
```

Run: `./run.sh --module 01`

---

### Module 02 — Streaming
**File:** `modules/02_streaming.py`

Real-time token streaming with TTFT (time-to-first-token) measurement. Dramatically improves perceived latency for long outputs.

```python
with client.messages.stream(
    model=model,
    max_tokens=1024,
    system="You are helpful.",
    messages=[{"role": "user", "content": "Write a 500-word story."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()
```

**Critical:** Always call `stream.get_final_message()` after iteration — it contains the `usage` and `stop_reason` that are not available during streaming.

Run: `./run.sh --module 02`

---

### Module 03 — Multi-Turn Chat
**File:** `modules/03_multi_turn.py`

Builds persistent conversation history. The key rule: **append the entire `response.content` to history** — not `extract_text()` — to preserve `thinking` blocks.

```python
history = []
while True:
    user_input = input("You: ")
    response = client.messages.create(
        model=model, max_tokens=1024,
        system="You are helpful.",
        messages=history + [{"role": "user", "content": user_input}]
    )
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response.content})
    # ... print response.text ...
```

Run: `./run.sh --module 03`

---

### Module 04 — Tool Use
**File:** `modules/04_tool_use.py`

Function calling with local dispatch. Tools are defined in Anthropic schema format:

```python
tools = [
    {
        "name": "calculator",
        "description": "Evaluate a math expression",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    }
]

response = client.messages.create(
    model=model, max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "What is 2**10?"}],
    tools=tools
)

# Detect tool calls
for block in response.content:
    if block.type == "tool_use":
        result = eval(block.input["expression"])
        history.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result)
            }]
        })
```

Run: `./run.sh --module 04`

---

### Module 05 — Extended Thinking
**File:** `modules/05_thinking.py`

Enables the model's interleaved reasoning chain. `response.content` will contain **both** `thinking` blocks and `text` blocks — both must be preserved in history.

```python
response = client.messages.create(
    model=model,
    max_tokens=4096,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Solve: why is the sky blue?"}],
    thinking={
        "type": "enabled",
        "budget_tokens": 3000   # must be < max_tokens
    }
)

# response.content[0].type == "thinking"
# response.content[1].type == "text"
```

> **Rule:** `max_tokens` must be strictly greater than `budget_tokens`. If equal, no tokens remain for the answer.

Run: `./run.sh --module 05`

---

### Module 06 — System Prompting
**File:** `modules/06_system_prompt.py`

Structured XML system prompts outperform bare strings. Uses four constraint tags:

```python
system = """
<persona>You are an expert code reviewer.</persona>
<scope>Python 3.10+, type annotated.</scope>
<output_format>JSON with fields: severity, line_number, suggestion</output_format>
<constraints>
- Never suggest deleting entire functions
- Always cite the relevant PEP or documentation
</constraints>
"""
```

Demonstrates bare vs structured prompting with side-by-side comparison and few-shot examples.

Run: `./run.sh --module 06`

---

### Module 07 — Cost Tracking
**File:** `modules/07_cost_tracker.py`

`CostLedger` class tracks every API call, accumulates usage, detects cache hits, and enforces budget limits.

```python
class CostLedger:
    def __init__(self, budget_usd: float):
        self.budget_usd = budget_usd
        self.total_cost = 0.0
        self.calls = 0

    def record(self, usage):
        inp = usage.input_tokens or 0
        out = usage.output_tokens or 0
        cr  = getattr(usage, "cache_read_input_tokens", 0) or 0
        cost = (inp/1e6)*0.30 + (out/1e6)*1.20
        self.total_cost += cost
        self.calls += 1
        if self.total_cost > self.budget_usd:
            raise RuntimeError(f"Budget exceeded: ${self.total_cost:.4f}")
```

> **Cache savings:** `cache_read_input_tokens` are charged at a reduced rate. Always include them in cost calculations.

Run: `./run.sh --module 07`

---

### Module 08 — Agent ReAct Loop
**File:** `modules/08_agent_loop.py`

Full ReAct (Reason → Act → Observe → Repeat) pattern with scratchpad memory:

```python
_SCRATCHPAD = {}

AGENT_TOOLS = {
    "search": lambda args: ...,
    "calculator": lambda args: ...,
    "remember": lambda args: (_SCRATCHPAD.update(args), "Remembered."),
    "recall": lambda args: _SCRATCHPAD.get(args["key"], "Not found."),
    "finish": lambda args: f"FINAL_ANSWER: {args['answer']}",
}

dispatch_map = {tool.name: tool for tool in AGENT_TOOLS.values()}

# Loop
for i in range(max_iterations):
    response = client.messages.create(model=model, max_tokens=4096,
        system=SYSTEM_PROMPT, messages=history, tools=TOOL_DEFS)
    for block in response.content:
        if block.type == "tool_use":
            result = dispatch_map[block.name](block.input)
            history.append({"role": "user", "content": [{
                "type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)
            }]})
            if result.startswith("FINAL_ANSWER:"):
                print(result); return
```

Run: `./run.sh --module 08`

---

## 5. Common Tasks

### Run all modules at once

```bash
./run.sh --all
```

### Run a range (modules 3–6)

```bash
./run.sh --all --from 03 --to 06
```

### Switch to China endpoint

```bash
# Via setup
./setup.sh --key YOUR_KEY --endpoint cn

# Via flag at runtime
./run.sh --module 01 --endpoint cn
```

### Switch to highspeed model

```bash
# Via setup
./setup.sh --key YOUR_KEY --highspeed

# Via runtime flag
./run.sh --module 01 --highspeed

# Via environment variable (edit .env)
MINIMAX_USE_HIGHSPEED=true
```

### Log output to a file

```bash
./run.sh --module 04 --log
# Output saved to logs/module-04-<timestamp>.log
```

### Check environment without running

```bash
./run.sh --check
```

### Dry run (print command without executing)

```bash
./run.sh --dry-run --module 04
```

### Use a custom .env file

```bash
./run.sh --env .env.staging --module 01
```

---

## 6. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *(required)* | Your MiniMax API key |
| `ANTHROPIC_BASE_URL` | `https://api.minimax.io/anthropic` | API endpoint |
| `MINIMAX_USE_HIGHSPEED` | `false` | Use highspeed variant |

---

## 7. Troubleshooting

### "No python or python3 found in PATH"

Install Python 3.10+ from [python.org](https://python.org). On macOS: `brew install python3`. On Ubuntu/Debian: `sudo apt install python3.10`. On Termux (Android): `pkg install python`.

### "Cannot import anthropic"

The venv is not activated. Run:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY is not set"

The `.env` file is missing or has a placeholder value. Re-run setup:

```bash
./setup.sh --key YOUR_KEY --force
```

### "budget_tokens must be less than max_tokens"

In module 05, `max_tokens` must be **greater than** `budget_tokens`. Set `max_tokens=4096` and `budget_tokens=3000`, for example.

### "thinking blocks not in history"

You called `extract_text()` or manually extracted only text blocks. Always append `response.content` verbatim:

```python
history.append({"role": "assistant", "content": response.content})
```

### "Module file not found"

Run from the `minimax_m27_tutorial/` directory:

```bash
cd minimax_m27_tutorial
./run.sh --module 01
```

---

## Next Steps

After completing the modules, you have working patterns for:

- Production API integration with streaming and cost tracking
- Reliable multi-turn agents with tool use
- Structured prompting with constraint tags

Adapt `config.py`, `utils.py`, and the module patterns to your own project. The shared utilities (`load_env`, `make_client`, `log`, `report_usage`, `print_blocks`) are designed to be copied directly into your codebase.
