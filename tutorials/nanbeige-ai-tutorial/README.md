# Nanbeige4.1-3B: Comprehensive Tutorial for AI Engineers

A practical, hands-on tutorial for **Nanbeige4.1-3B** — a 3-billion-parameter open-source model that rivals 30B+ models in reasoning, code generation, and agentic tool use.

## Benchmark Highlights

| Benchmark | Nanbeige4.1-3B | Qwen3-30B-A3B | Qwen3-32B |
|---|---|---|---|
| LiveCodeBench | **76.9** | 66.0 | 68.3 |
| GPQA-Diamond | **82.2** | 73.4 | 68.7 |
| AIME 2024 (avg@8) | **90.4** | 89.2 | 81.4 |
| AIME 2025 (avg@8) | **85.6** | 85.0 | 72.9 |
| BFCL-V4 (Tool Use) | **53.8** | 48.6 | — |
| Arena-Hard V2 | **73.8** | — | — |

## Key Features

- **Agentic Tool Use** — up to 600 tool-call turns per session
- **Chain-of-Thought Reasoning** — `<think>` blocks for transparent reasoning
- **Code Generation** — LiveCodeBench performance comparable to DeepSeek R1 (670B)
- **Complexity-Aware RL** — trained with difficulty-scaled reward signals
- **Apache 2.0 License** — fully open source

## What's Included

| File | Description |
|---|---|
| `nanbeige_tutorial.ipynb` | 12-section interactive notebook covering all capabilities |
| `app.py` | Gradio web UI with multi-mode chat (Code, Reasoning, Tool Use) |
| `pyproject.toml` | uv project configuration with optional extras |

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- GPU with 6-8 GB VRAM (FP16) or CPU with 8+ GB RAM

### Setup & Run

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and navigate
cd tutorials/nanbeige-ai-tutorial

# Install dependencies
uv sync

# Run the interactive notebook
uv run jupyter notebook nanbeige_tutorial.ipynb

# Run the Gradio web app
uv run python app.py
# Opens at http://localhost:7860
```

### Optional Extras

```bash
# vLLM for production serving
uv sync --extra vllm
uv run vllm serve Nanbeige/Nanbeige4.1-3B \
    --trust-remote-code \
    --enable-reasoning \
    --reasoning-parser deepseek_r1

# Quantization support (INT4/INT8)
uv sync --extra quantize
```

## Tutorial Sections (Notebook)

1. **Introduction & Architecture** — Model overview, training techniques, benchmarks
2. **Environment Setup** — uv setup, GPU requirements
3. **Model Loading** — AutoModel, Pipeline, device-aware loading
4. **Reasoning & CoT** — Math (AIME-style), science (GPQA-style), logic puzzles
5. **Code Generation** — Algorithms, data pipelines, debugging
6. **Agentic Tool Use** — Tool schemas, execution loops, multi-tool chains
7. **Multi-Turn Conversations** — Context tracking over extended dialogues
8. **Benchmarking** — Custom mini-benchmark suite across categories
9. **Quantization** — INT8/INT4 with bitsandbytes
10. **vLLM Deployment** — Production server with OpenAI-compatible API
11. **Temperature Experiments** — Sampling parameter impact analysis
12. **Tips & Limitations** — Production recommendations and known issues

## Gradio App Features

- **5 Modes**: General Chat, Code Assistant, Math & Reasoning, Science Expert, Tool Use Agent
- **Adjustable Parameters**: Temperature, top-p, max tokens
- **Thinking Display**: Toggle `<think>` block visibility
- **Tool Call Simulation**: See structured tool calls with mock execution
- **Conversation Management**: Clear, retry, full history

## Recommended Settings

| Use Case | Temperature | top_p | Notes |
|---|---|---|---|
| Code generation | 0.6 | 0.95 | Best balance of correctness/variety |
| Math/reasoning | 0.6 | 0.95 | Let the model think deeply |
| Creative writing | 0.5-0.6 | 0.95 | Community-reported sweet spot |
| Factual Q&A | 0.0 | 1.0 | Greedy for deterministic answers |
| Tool calling | 0.6 | 0.95 | Structured output needs flexibility |

## Known Limitations

- **No official GGUF** — Use community versions: [DevQuasar GGUF](https://huggingface.co/DevQuasar/Nanbeige.Nanbeige4.1-3B-GGUF)
- **Extended coding bugs** — Occasional errors in very long multi-step tasks
- **32K context** — Long tool-call chains can approach the limit
- **Benchmark validation** — Authors may select checkpoints using evaluation benchmarks

## References

- [HuggingFace Model Card](https://huggingface.co/Nanbeige/Nanbeige4.1-3B)
- [Technical Report (arXiv)](https://arxiv.org/html/2602.13367v1)
- [Community GGUF](https://huggingface.co/DevQuasar/Nanbeige.Nanbeige4.1-3B-GGUF)
- [Ollama Model](https://ollama.com/fauxpaslife/nanbeige4.1-python-deepthink:3b-q8)
- [vLLM Documentation](https://docs.vllm.ai)

## License

Apache 2.0 — Same as the model itself.
