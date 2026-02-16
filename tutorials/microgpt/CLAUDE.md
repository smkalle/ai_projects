# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MicroGPT is an educational tutorial implementing a complete GPT language model from scratch. Two parallel implementations exist: pure Python (zero dependencies) and PyTorch. Based on Andrej Karpathy's minimal GPT implementation. Trains a character-level language model on ~32K baby names to generate new plausible names.

## Commands

### Pure Python (no dependencies)

```bash
python test_microgpt.py           # Run tests
python microgpt_simple.py         # Train and generate (~5-10 min)
python _run_notebook.py           # Notebook as script
jupyter notebook microgpt_tutorial.ipynb
```

### PyTorch (use uv for all package management and execution)

```bash
uv sync                                    # Install dependencies
uv run python test_microgpt_pytorch.py     # Run tests
uv run python microgpt_pytorch.py          # Train and generate (~30s)
uv run jupyter notebook microgpt_pytorch_tutorial.ipynb
```

## Architecture

The entire implementation uses only 6 atomic scalar operations (`+`, `*`, `**`, `log`, `exp`, `relu`) with a ~30-line autograd engine.

### Core Pipeline

Input characters → character-level tokenization (27 vocab: a-z + BOS) → token + position embeddings (dim 16) → RMSNorm → multi-head self-attention (4 heads) → residual → RMSNorm → MLP (16→64→16 with ReLU) → residual → linear output (→27) → softmax → next token prediction

### Key Components in `microgpt_simple.py`

- **`Value` class**: Autograd engine that wraps scalars, tracks computation graphs, and computes gradients via reverse-mode autodiff (topological sort + chain rule)
- **`linear()`/`softmax()`/`rmsnorm()`**: Stateless functions operating on lists of `Value` objects
- **Model parameters**: ~8,000 total parameters stored as flat lists of `Value` objects (not in classes)
- **Adam optimizer**: Implemented from scratch with momentum (β₁=0.85), second moment (β₂=0.99), bias correction, and linear LR decay
- **Forward pass**: The `gpt()` function wires everything together—embeddings, attention, MLP, output projection
- **Generation**: Autoregressive sampling with temperature control

### Design Decisions

- All tensors are represented as nested Python lists of `Value` objects—there are no matrix/tensor abstractions
- The model has 1 transformer layer, context window of 16 characters
- Training processes one name per step (no batching)
- `input.txt` (names dataset) is auto-downloaded from GitHub if missing

## File Roles

### Pure Python
- `microgpt_simple.py` — self-contained training script (~330 lines), the canonical implementation
- `microgpt_tutorial.ipynb` — 10-part interactive tutorial with explanations and visualizations
- `_run_notebook.py` — the notebook exported as a Python script with additional analysis (gradient flow, attention patterns)
- `test_microgpt.py` — unit tests for autograd, tokenizer, model components, initialization, and forward pass

### PyTorch
- `microgpt_pytorch.py` — PyTorch training script, same architecture and 7-section structure as pure Python
- `microgpt_pytorch_tutorial.ipynb` — 10-part PyTorch tutorial with matplotlib visualizations (attention heatmaps, loss curves)
- `test_microgpt_pytorch.py` — PyTorch tests for autograd, tokenizer, components, model, and forward pass
- `pyproject.toml` — uv project config with torch and matplotlib dependencies
