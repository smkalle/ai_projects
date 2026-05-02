# RecursiveMAS — Latent-Space Recursive Multi-Agent Systems

> Implementation tutorial and CLI demo for the paper **"RecursiveMAS: Recursive Multi-Agent Systems via Latent State Transfer"** (arXiv:2604.25917, April 2026).

---

## What is RecursiveMAS?

Traditional multi-agent systems (MAS) pass **text** between agents. Every handoff is a full token sequence — quadratic context growth, latency spikes, and semantic dilution. RecursiveMAS eliminates the token tax entirely.

**The core idea:** treat the entire agent pipeline as a single *recursive language model* (RLM). Agents are layers. Communication is direct latent-state transfer via a lightweight learned projector called **RecursiveLink**. Only the final agent in the final recursion round decodes to text.

### Results (9 benchmarks: MATH500, AIME, GPQA, MedQA, LiveCodeBench, HotpotQA, ...)

| Metric | Gain vs. text-MAS baseline |
|--------|---------------------------|
| Accuracy | +8.3% average |
| Token usage | -34.6% to -75.6% |
| Inference speed | 1.2–2.4× faster |
| Trainable params | ~13M (0.31% of system) |

---

## Architecture

```
Input text
  └─► Agent 0 (Planner)  embed_tokens → h [B, L, 1536]
        └─► inner_link[0](h)           # self-refinement
              └─► outer_link[0](h)     # 1536 → 2048
                    └─► Agent 1 (Critic)  model(inputs_embeds=h) → h [B, 1, 2048]
                          └─► inner_link[1](h)
                                └─► outer_link[1](h)  # 2048 → 2304
                                      └─► Agent 2 (Solver)  model(inputs_embeds=h) → h [B, 1, 2304]
                                            └─► inner_link[2](h)
                                                  └─► [repeat r times; loop-close via outer_link[2]: 2304→1536]
                                                        └─► [final round only] lm_head(h) → decode → output
```

### RecursiveLink (the 13M-param core)

```
RecursiveLink(in_dim, out_dim, hidden_dim):
  residual = Linear(in_dim, out_dim)   # or Identity when dims match
  mlp      = Linear → GELU → Linear
  forward  = residual(h) + mlp(h)      # residual is mandatory — not just MLP
```

- **InnerLink**: `in_dim == out_dim` — per-agent latent thought refinement.
- **OuterLink**: `in_dim → out_dim` — cross-agent state transfer (handles dim mismatch).
- **Loop-close**: `outer_links[-1]` bridges last agent back to first agent between rounds.

### Target models (Sequential pattern, fits on 16 GB VRAM)

| Role | Model | Hidden dim |
|------|-------|-----------|
| Planner | `Qwen/Qwen2.5-Math-1.5B` | 1536 |
| Critic | `meta-llama/Llama-3.2-1B` | 2048 |
| Solver | `google/gemma-2-2b` | 2304 |

---

## Project Layout

```
recursivemas/
├── recursive_link.py     # RecursiveLink nn.Module (two-layer residual MLP)
├── mas_system.py         # RecursiveMAS orchestrator (loads agents, runs recursion)
├── train.py              # inner_loop_train() + outer_loop_train()
├── infer.py              # load_mas(), run_query(), probe_latent(), text_mas_baseline()
├── cli.py                # typer entry point: run / train / bench
├── config.yaml           # model names, recursion_depth, device settings
├── requirements.txt
├── AGENTS.md             # coding agent spec (repo build instructions)
├── TECH_SPEC.md          # full technical specification with tensor shape contracts
└── recursive_multiagent_system.MD  # tutorial writeup (L6 AI Engineer deep-dive)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run a single query

Models are downloaded automatically on first run (~5 GB total).

```bash
python cli.py run "What is 15% of 240?"
```

Output:
```
┌─ Round 1 ──────────────────────────┐
│ [Planner] processing latent...     │
│ [Critic]  processing latent...     │
│ [Solver]  processing latent...     │
└────────────────────────────────────┘
...
Answer: 36
Tokens decoded: 2  |  Latency: 380 ms
```

### 3. Debug with intermediate latent probes

```bash
python cli.py run "Solve for x: 2x + 5 = 13" --probe
```

### 4. Train link weights on MATH500

```bash
python cli.py train --dataset math500 --inner-epochs 3 --outer-epochs 5
```

Only `~13M` link parameters are trained. Checkpoints saved to `checkpoints/links_epoch{N}.pt`.

### 5. Benchmark vs. text-MAS baseline

```bash
python cli.py bench --dataset math500 --num-samples 50
```

```
                 RecursiveMAS    Text-MAS Baseline
Accuracy             72.0%           63.8%
Avg tokens/query       8              47
Avg latency          410 ms          890 ms
```

### CPU / low-VRAM mode

```bash
python cli.py run "Solve: integral of x^2 from 0 to 1" --cpu
```

Uses `float32`, `recursion_depth=1`, loads one agent at a time.

---

## CLI Reference

```
python cli.py run    QUESTION [--config PATH] [--checkpoint PATH] [--probe] [--cpu]
python cli.py train  [--dataset math500] [--inner-epochs 3] [--outer-epochs 5]
                     [--batch-size 4] [--lr 1e-4] [--config PATH] [--cpu]
python cli.py bench  [--dataset math500] [--num-samples 50] [--config PATH]
                     [--checkpoint PATH] [--cpu]
```

---

## Configuration (`config.yaml`)

```yaml
agents:
  - model_name: Qwen/Qwen2.5-Math-1.5B
    role: Planner
  - model_name: meta-llama/Llama-3.2-1B
    role: Critic
  - model_name: google/gemma-2-2b
    role: Solver

recursion_depth: 3      # paper sweet spot; use 1 for CPU demo
hidden_dim: 512         # RecursiveLink MLP inner dim (~13M params with SLMs)
device: auto            # "auto" | "cpu" | "cuda:0"
dtype: bfloat16         # "bfloat16" | "float32" (float32 required for CPU)
checkpoint_dir: checkpoints/
```

---

## Training Algorithm

Training happens in two phases, in order:

**Inner loop** (warm-start, per-link):
```
loss = 1 - cosine_similarity(inner_link(latent_h), embed(answer), dim=-1).mean()
```
Each inner link independently learns to align its output latent toward the target answer embedding.

**Outer loop** (joint, full system):
```
loss = cross_entropy(lm_head(RecursiveMAS(question)), answer_tokens)
```
All inner and outer links are optimized jointly with shared gradients through the full recursion.

Key invariant: **base LLM weights are always frozen.** Only RecursiveLink weights (~13M) are trained.

---

## Critical Implementation Notes

- `model.model(inputs_embeds=h, use_cache=False)` — KV cache must be disabled during latent recursion.
- Always take the **last token** hidden state after each agent: `h = outputs.last_hidden_state[:, -1:, :]`.
- Loop-close (`outer_links[-1]`) only fires when `r > 0`.
- Inner loop **must complete before** outer loop begins.
- `hidden_dim=512` targets ~13M trainable params with the SLM trio above.

---

## Tensor Shape Contract

| Transition | Shape | dtype |
|------------|-------|-------|
| After `embed_tokens` (Agent 0 input) | `[B, L, 1536]` | model dtype |
| After each agent forward | `[B, 1, d_i]` | same |
| After `inner_link` | `[B, 1, d_i]` | same |
| After `outer_link` | `[B, 1, d_{i+1}]` | same |
| Into `lm_head` | `[B, 1, d_N]` | same |

`B=1` for inference; batch dimension preserved for training.

---

## Testing

```bash
pytest
```

Tests (using tiny random mock models — no real model downloads in CI):

| Test | Asserts |
|------|---------|
| `test_recursive_link_shapes` | Output shape matches `out_dim` |
| `test_recursive_link_residual` | Residual contributes non-zero |
| `test_mas_forward_smoke` | Forward returns non-empty string |
| `test_no_base_grad` | Base model params have `requires_grad=False` |
| `test_latent_shape_contract` | Shape at each stage matches contract |
| `test_checkpoint_roundtrip` | Save + load; state dict keys match |

---

## Requirements

```
torch>=2.4.0
transformers>=4.44.0
accelerate>=0.33.0
datasets>=2.20.0
peft>=0.12.0
typer>=0.12.0
rich>=13.7.0
pyyaml>=6.0
```

Hardware: single GPU with ≥16 GB VRAM (bfloat16) or CPU (float32, depth=1).

---

## Key Concepts from the Paper

| Concept | Description |
|---------|-------------|
| **RecursiveMAS** | MAS treated as a single recursive language model (RLM) at system scale |
| **RecursiveLink** | Two-layer residual MLP projector for latent state transfer |
| **InnerLink** | Self-refinement within one agent's hidden space |
| **OuterLink** | Cross-agent transfer; handles hidden dimension mismatches |
| **Inner-outer loop** | Two-phase training: per-link cosine warm-start, then joint CE |
| **Late decoding** | Only the final agent in the final round decodes to text |
| **Loop-close** | Last agent's latent is fed back to first agent between rounds |
| **Recursion depth `r`** | Number of full pipeline passes; depth 3 is the paper's sweet spot |

---

## Collaboration Patterns

RecursiveLink supports multiple agent topologies — the same framework handles:

- **Sequential** (this demo): Planner → Critic → Solver
- **Mixture-of-Experts**: route latent to specialist agents
- **Deliberation**: same agent group iterates until convergence
- **Distillation**: large teacher agent → small student agent via latent

---

## Paper Reference

```bibtex
@misc{recursivemas2026,
  title  = {RecursiveMAS: Recursive Multi-Agent Systems via Latent State Transfer},
  year   = {2026},
  note   = {arXiv:2604.25917}
}
```

---

## Docs

- `recursive_multiagent_system.MD` — full L6 AI Engineer tutorial with step-by-step implementation walkthrough
- `TECH_SPEC.md` — complete technical specification: tensor shapes, module APIs, error handling, performance targets
- `AGENTS.md` — coding agent build spec (for AI-assisted development)

---

## License

MIT
