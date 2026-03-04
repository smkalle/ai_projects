# Changelog

## 0.1.0 (2026-03-04)

Initial release.

### Features

- Interactive terminal REPL with streaming output
- Local HuggingFace model loading (Qwen-focused)
- Auto device detection: CUDA, MPS, CPU
- 4-bit and 8-bit quantization via BitsAndBytes (CUDA)
- Chat history save/load as JSON
- Runtime parameter tuning (temperature, top_p, max_new_tokens)
- Slash commands: `/help`, `/clear`, `/save`, `/load`, `/system`, `/set`, `/exit`
- System prompt customization
- Colab notebook with full capability demonstration

### Architecture

- Three-module design: `session.py` (data), `engine.py` (inference), `cli.py` (UI)
- Unit tests covering CLI and session logic
- Capability test suite for real model validation
