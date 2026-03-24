# Quick Start

Get up and running in 2 minutes.

## 1. Clone & Setup

```bash
git clone <repo-url>
cd code_eval_workbench
./setup.sh
```

`setup.sh` installs dependencies with `uv sync` and creates `.env` from `.env.example`.

## 2. Add Your API Key

Open `.env` and set your key:

```env
# Claude (default)
ANTHROPIC_API_KEY=sk-ant-...

# OR MiniMax M2.7
# ANTHROPIC_API_KEY=<your-minimax-key>
# ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
```

Get your key at [console.anthropic.com](https://console.anthropic.com) or [platform.minimax.io](https://platform.minimax.io).

## 3. Run

**Web UI** (recommended for exploration):
```bash
./run.sh
# Opens at http://localhost:8501
```

**CLI** (headless, great for automation):
```bash
./run.sh cli
```

## 4. Run Tests

```bash
./verify.sh
```

## What's Next?

- **Filter examples**: `./run.sh cli --category arithmetic --difficulty easy`
- **Skip slow scorers**: `./run.sh cli --no-llm --no-prog`
- **Set a CI threshold**: `./run.sh cli --threshold 0.70`
- **Export results**: `./run.sh cli --output results.json`
- **Generate more dataset examples**: use the **Dataset Studio** tab in the web UI
- **Swap to MiniMax**: uncomment the MiniMax lines in `.env` — no other changes needed
