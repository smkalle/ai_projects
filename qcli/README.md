# qcli

A local-first terminal chat app for running Hugging Face language models (Qwen-focused) entirely on-device. No hosted API, no cloud dependency.

## Features

- **Local inference** — runs Qwen3.5-2B (or any HF causal LM) on your hardware
- **Streaming output** — token-by-token display as the model generates
- **Multi-device** — auto-detects CUDA, MPS (Apple Silicon), or CPU
- **4-bit / 8-bit quantization** — via BitsAndBytes for memory-constrained GPUs
- **Chat history** — save/load conversations as JSON, resume later
- **Runtime tuning** — adjust temperature, top_p, max_new_tokens mid-session
- **Slash commands** — `/help`, `/clear`, `/save`, `/load`, `/system`, `/set`, `/exit`

## Quick Start

```bash
# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# Run
qcli --model Qwen/Qwen3.5-2B
```

## Installation

### Basic

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Development (pytest + ruff)

```bash
pip install -e '.[dev]'
```

### Quantization (CUDA only)

```bash
pip install -e '.[quant]'
```

### Using uv (lockfile included)

```bash
uv sync
```

## Usage

```bash
# Default model
qcli --model Qwen/Qwen3.5-2B

# Custom parameters
qcli --model Qwen/Qwen3.5-2B --temperature 0.7 --top-p 0.9 --max-new-tokens 512

# Custom system prompt
qcli --model Qwen/Qwen3.5-2B --system "You are concise and technical."

# Resume a saved session
qcli --model Qwen/Qwen3.5-2B --history-file chat.json

# Quantized inference on CUDA
qcli --model Qwen/Qwen3.5-2B --device cuda --quantized 4bit

# Low-RAM mode
qcli --model Qwen/Qwen3.5-2B --max-new-tokens 128 --temperature 0.6
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `Qwen/Qwen3.5-2B` | HuggingFace model ID |
| `--temperature` | `0.7` | Sampling temperature (0 = deterministic) |
| `--top-p` | `0.9` | Nucleus sampling threshold |
| `--max-new-tokens` | `512` | Maximum tokens to generate |
| `--system` | `You are a helpful assistant.` | System prompt |
| `--device` | `auto` | `auto`, `cpu`, `cuda`, or `mps` |
| `--dtype` | `auto` | `auto`, `float16`, `bfloat16`, or `float32` |
| `--quantized` | `none` | `none`, `4bit`, or `8bit` (CUDA only) |
| `--trust-remote-code` | off | Allow model's custom Python code |
| `--history-file` | none | JSON file to load/save session |
| `--no-stream` | off | Disable streaming (collect then print) |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Clear history (keeps system prompt) |
| `/save <path>` | Save conversation to JSON |
| `/load <path>` | Load conversation from JSON |
| `/system <text>` | Set a new system prompt |
| `/set temperature <float>` | Adjust temperature |
| `/set top_p <float>` | Adjust top_p |
| `/set max_new_tokens <int>` | Adjust output length |
| `/exit` | Quit |

## Architecture

Three-module design in `qcli/`:

```
qcli/
├── session.py   # Pure data: ChatSession, GenerationConfig, JSON save/load
├── engine.py    # Model loading, device detection, streaming inference
└── cli.py       # Argparse CLI, REPL loop, slash command dispatch
```

## Colab Notebook

Try Qwen3.5-2B without any local setup:

**[`notebooks/qwen3_5_capabilities.ipynb`](notebooks/qwen3_5_capabilities.ipynb)** — a self-contained Colab notebook that demonstrates all capabilities: instruction following, system prompts, multi-turn chat, temperature/sampling control, streaming, code generation, robustness, 4-bit quantization, and session persistence.

## Testing

```bash
# Unit tests (no GPU needed)
pytest

# Single test
pytest tests/test_session.py::test_save_load_roundtrip

# Capability tests (requires model download)
python scripts/test_qwen_capabilities.py --model Qwen/Qwen2.5-0.5B-Instruct --device cpu -v

# Lint
ruff check .
ruff format .
```

## Platform Notes

- First model download is large (~4GB for 2B params) and requires network access
- `--quantized 4bit|8bit` requires CUDA and `bitsandbytes`
- On Termux/proot: use `transformers<4.50` and `accelerate<1.0` (see pyproject.toml)
- For low-RAM devices, reduce `--max-new-tokens` and use smaller models

## License

[MIT](LICENSE)
