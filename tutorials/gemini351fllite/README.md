# Gemini 3.1 Flash-Lite Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A CLI and Streamlit app to explore the full capabilities of Google's **Gemini 3.1 Flash-Lite** — their most cost-efficient model with thinking levels, multimodal support, and strong benchmarks.

## Features

- **Interactive Chat** — Multi-turn streaming conversations
- **Thinking Levels** — Compare MINIMAL / LOW / MEDIUM / HIGH reasoning depth side-by-side
- **Vision** — Image analysis and description
- **Audio** — Transcription and summarization
- **Structured Output** — JSON generation with Pydantic schemas
- **Function Calling** — Tool use with automatic execution
- **Embeddings** — Text similarity via cosine distance
- **Benchmarks** — Latency and token usage across thinking levels
- **API Trace Log** — Full request/response logging to console

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/smkalle/gemini351fllite.git
cd gemini351fllite
./setup.sh

# 2. Add your API key
# Edit .env and set GEMINI_API_KEY
# Get a key at: https://aistudio.google.com/apikey

# 3. Run
./run_cli.sh chat              # Interactive CLI chat
./run_cli.sh --help            # See all commands
./run_app.sh                   # Launch Streamlit web app
```

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `chat` | Interactive streaming chat | `./run_cli.sh chat --level high` |
| `think` | Compare thinking levels | `./run_cli.sh think "Explain entropy"` |
| `vision` | Analyze an image | `./run_cli.sh vision photo.jpg` |
| `audio` | Transcribe/summarize audio | `./run_cli.sh audio recording.mp3` |
| `json` | Structured JSON output | `./run_cli.sh json --prompt "A pasta recipe"` |
| `tools` | Function calling demo | `./run_cli.sh tools "Weather in Tokyo?"` |
| `embed` | Text similarity | `./run_cli.sh embed "cats" "kittens"` |
| `bench` | Benchmark thinking levels | `./run_cli.sh bench --rounds 3` |

## Streamlit App

Launch with `./run_app.sh` and open http://localhost:8501.

The sidebar provides navigation to all 8 capability pages. Each page includes configurable thinking levels and displays results with token usage. API traces print to the terminal for debugging.

## Project Structure

```
gemini_explorer/
  client.py    # Shared client, config helpers, API tracing
  cli.py       # Click CLI with 8 subcommands
  app.py       # Streamlit app with 8 pages
samples/       # Place test images/audio here
setup.sh       # Install dependencies (uv + pip)
run_cli.sh     # Launch CLI
run_app.sh     # Launch Streamlit
```

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (auto-installed by setup.sh)
- A [Gemini API key](https://aistudio.google.com/apikey)

## License

[MIT](LICENSE)
