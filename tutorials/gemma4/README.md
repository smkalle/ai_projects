# Gemma 4 CLI

> Interactive chat for AI engineers — all four model sizes, multimodal, native function calling, 256K context, offline code gen, 140+ languages. Apache 2.0.

---

## Fastest path: 3 commands

```bash
git clone <this-repo> && cd gemma4-cli
chmod +x setup.sh run.sh
./setup.sh          # installs everything: Python env, Ollama, pulls gemma4:e4b
./run.sh            # launch
```

`setup.sh` is idempotent — safe to re-run any time.

---

## Setup options

```bash
./setup.sh                        # default: pulls gemma4:e4b
./setup.sh --model 31b            # pull 31B instead
./setup.sh --all-models           # pull all four variants
./setup.sh --skip-pull            # env only, pull models later
./setup.sh --force                # rebuild virtualenv from scratch
./setup.sh --dry-run              # preview every action, run nothing
```

| Flag | Default | Purpose |
|------|---------|---------|
| `--model e2b\|e4b\|26b\|31b` | `e4b` | Which model to pull |
| `--all-models` | — | Pull all four |
| `--skip-ollama` | — | Don't install Ollama |
| `--skip-pull` | — | Skip model pull |
| `--skip-venv` | — | Use system Python |
| `--python <bin>` | auto | Specific Python binary |
| `--ollama-url <url>` | `localhost:11434` | Remote Ollama endpoint |
| `--force` | — | Re-run even if already done |
| `--dry-run` | — | Print, don't execute |

---

## Run options

### Presets — one flag, full configuration

```bash
./run.sh                          # defaults from .env (e4b, temp 0.7, 32K ctx)
./run.sh --max                    # 31B + 256K context
./run.sh --agent                  # 26B MoE + function calling
./run.sh --code-mode              # e4b + SDE3 prompt + temp 0.2
./run.sh --edge                   # e2b, minimum VRAM (~3.2 GB)
./run.sh --multilingual Kannada   # system prompt → "Reply only in Kannada"
```

### All flags

```bash
# Model & generation
./run.sh --model 31b
./run.sh --ctx 262144             # 256K context (26b/31b only)
./run.sh --temp 0.2               # deterministic output
./run.sh --tools                  # function calling on from start
./run.sh --system "Be concise"    # custom system prompt

# Ollama lifecycle
./run.sh --pull-first             # refresh model before launching
./run.sh --ollama-url http://gpu-box:11434   # remote Ollama
./run.sh --gpu-layers 35          # GPU/CPU layer split
./run.sh --no-start-ollama        # fail fast if Ollama not running
./run.sh --stop-ollama            # kill Ollama when CLI exits
./run.sh --wait-ollama 60         # extend startup timeout (seconds)

# Sessions & logging
./run.sh --log                    # write session to logs/session_<ts>.log
./run.sh --load my_chat.json      # resume a saved conversation

# Combine freely
./run.sh --max --tools --log
./run.sh --model 26b --ctx 131072 --temp 0.3 --tools --pull-first
./run.sh --dry-run                # print exact Python command, run nothing
```

---

## Models

| Key | Tag | Params | Context | VRAM | Best for |
|-----|-----|--------|---------|------|---------|
| `e2b` | `gemma4:e2b` | 2B eff. | 128K | ~3.2 GB | Mobile / edge / Pi |
| `e4b` | `gemma4:e4b` | 4B eff. | 128K | ~5 GB | Laptops — **start here** |
| `26b` | `gemma4:26b` | 4B active / 26B total (MoE) | 256K | ~15.6 GB | Agents / throughput |
| `31b` | `gemma4:31b` | 31B dense | 256K | ~17.4 GB | Best quality |

License: Apache 2.0 — commercial use OK, your code stays private.

---

## In-chat commands

Once inside `./run.sh`, type at any prompt:

```
/model 31b              switch model mid-session
/tools                  toggle function calling on/off
/image /path/img.png    attach image to next message (multimodal)
/code-mode              SDE3 code generation mode
/system <prompt>        update system prompt
/ctx 262144             change context window live
/temp 0.5               change temperature live
/context                token usage stats
/clear                  clear history, keep system prompt
/save [file]            save conversation → JSON
/load file.json         resume conversation
/export [file]          export → Markdown
/specs                  model comparison table
/models                 list Ollama-installed models
/pull gemma4:31b        pull a model without leaving the chat
/help                   full command reference
/quit                   exit
```

---

## Common workflows

**Multimodal — analyze an image:**
```
/image /path/to/architecture.png
What are the single points of failure in this diagram?
```

**Agentic tool use:**
```bash
./run.sh --agent
# inside chat:
What is sqrt(8192) and should I bring an umbrella in Bangalore tomorrow?
# → model calls calculate + get_weather, synthesizes a final answer
```

**256K long-context code review:**
```bash
./run.sh --max --tools
/image /path/to/diagram.png
Walk me through this system and identify race conditions
```

**Offline code generation:**
```bash
./run.sh --code-mode
Write a FastAPI JWT auth service with refresh tokens and Redis session store
```

**Multilingual:**
```bash
./run.sh --multilingual Tamil
# or set live:
/system You are a Hindi grammar tutor. Reply only in Hindi.
```

**Resume a saved session:**
```bash
./run.sh --load sessions/my_chat.json
# or inside any active session:
/load sessions/my_chat.json
```

---

## Configuration — `.env`

Generated by `setup.sh`. Edit to change persistent defaults:

```bash
GEMMA4_DEFAULT_MODEL=e4b          # e2b | e4b | 26b | 31b
GEMMA4_TEMPERATURE=0.7
GEMMA4_CTX_SIZE=32768             # 131072 = 128K  |  262144 = 256K
GEMMA4_TOOLS_ENABLED=false
GEMMA4_SYSTEM_PROMPT=             # leave blank for built-in engineer prompt
OLLAMA_HOST=http://localhost:11434
GEMMA4_SESSIONS_DIR=./sessions
GEMMA4_LOG_DIR=./logs
GEMMA4_VENV_DIR=./.venv
```

Any `run.sh` flag overrides the `.env` value for that session only.

---

## Architecture

```
gemma4-cli/
├── setup.sh              One-time bootstrap (OS, venv, Ollama, model pull)
├── run.sh                Launch script (presets, Ollama lifecycle, flag pass-through)
├── gemma4_cli.py         Core CLI
│   ├── OllamaClient          Streaming REST wrapper
│   ├── ConversationManager   History, token stats, save/load/export
│   ├── Tool layer            5 built-in tools + agentic loop (8 rounds max)
│   └── Gemma4CLI             Rich TUI, command dispatcher, streaming chat
├── requirements.txt
├── .env                  Runtime config (auto-generated)
├── logs/                 Ollama + session logs
└── sessions/             Saved conversations (JSON)
```

---

## Troubleshooting

**Ollama not starting:**
```bash
ollama serve                       # start manually in a separate terminal
./run.sh --wait-ollama 60          # or extend the timeout
```

**Model not found:**
```bash
./run.sh --pull-first              # pull before launch
ollama pull gemma4:e4b             # or pull directly
```

**Out of VRAM:**
```bash
./run.sh --edge                    # e2b: ~3.2 GB
./run.sh --gpu-layers 0            # CPU-only mode
```

**Function calling not triggering:**  
Add to your system prompt: *"When using tools, always respond in JSON tool-call format."*  
Then toggle with `/tools` and re-ask.

**Re-run setup after update:**
```bash
./setup.sh --force
```
