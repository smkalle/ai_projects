# AGENTS.md — recursiveMAS

## Repo state

This repo contains **one source document** and no runnable code yet:
- `recursive_multiagent_system.MD` — tutorial writeup for the RecursiveMAS paper (arXiv:2604.25917)

All four source files described in the tutorial (`recursive_link.py`, `mas_system.py`, `train.py`, `infer.py`) still need to be created.

---

## What this project is

RecursiveMAS replaces text-passing between agents with **direct latent-state transfer**. Agents never exchange tokens mid-pipeline; only the final agent in the final recursion round decodes to text. The entire system is trained as a single recursive language model (RLM).

Key invariant: **base LLMs are always frozen**. Only `RecursiveLink` weights (~13M params total) are trained.

---

## CLI App Spec — Multi-Stage SLM Pipeline Demo

Goal: a self-contained CLI app that demonstrates the RecursiveMAS tutorial using SLMs (≤2B params each), runnable on a single consumer GPU or CPU with reduced precision.

### Target models (SLMs, fits on 16 GB VRAM together)

| Role | Model | Hidden dim |
|------|-------|-----------|
| Planner | `Qwen/Qwen2.5-Math-1.5B` | 1536 |
| Critic | `meta-llama/Llama-3.2-1B` | 2048 |
| Solver | `google/gemma-2-2b` | 2304 |

Outer links bridge the dim mismatches (1536→2048, 2048→2304, 2304→1536 for loop-close).

### Project layout to create

```
recursivemas/
├── recursive_link.py     # RecursiveLink nn.Module (two-layer residual MLP)
├── mas_system.py         # RecursiveMAS orchestrator (loads agents, runs recursion)
├── train.py              # inner_loop_train() + outer_loop_train()
├── infer.py              # standalone inference helpers
├── cli.py                # entry point (see spec below)
├── config.yaml           # model names, recursion_depth, device settings
└── requirements.txt      # torch, transformers, accelerate, datasets, peft, rich, typer
```

### CLI interface (`cli.py`)

Use `typer` + `rich` for output. Three sub-commands:

```
python cli.py run    "Solve: integral of x^2 from 0 to 1"
python cli.py train  --dataset math500 --inner-epochs 3 --outer-epochs 5
python cli.py bench  --dataset math500 --num-samples 50
```

**`run` behaviour:**
- Load models (with `device_map="auto"`, `torch_dtype=torch.bfloat16`)
- Print a live panel per recursion round showing which agent is processing
- Optionally `--probe` flag: decode intermediate latents to text for debugging (every round)
- Print final decoded answer with token count and latency

**`train` behaviour:**
- Run inner loop first (per-link cosine warm-start), then outer loop (full CE)
- Save only link weights to `checkpoints/links_epoch{N}.pt` (not full model)
- Log loss per epoch to stdout

**`bench` behaviour:**
- Run `run` over N samples, compare to ground truth
- Print accuracy, avg tokens used, avg latency vs. a text-MAS baseline (sequential prompt-chaining)

### Multi-stage pipeline data flow

```
Input text
  └─► Agent 0 (Planner): embed_tokens → h [B, L, 1536]
        └─► inner_link[0](h) → refined h
              └─► outer_link[0](h): 1536→2048
                    └─► Agent 1 (Critic): model(inputs_embeds=h) → h [B, 1, 2048]
                          └─► inner_link[1](h)
                                └─► outer_link[1](h): 2048→2304
                                      └─► Agent 2 (Solver): model(inputs_embeds=h) → h [B, 1, 2304]
                                            └─► inner_link[2](h)
                                                  └─► [repeat r times, loop-close: outer_link[2] 2304→1536]
                                                        └─► [final round only] lm_head(h) → decode → output
```

### Critical implementation notes

- `model.model(inputs_embeds=h, use_cache=False)` — always disable KV cache during latent recursion
- Take only the **last token** hidden state after each agent: `h = outputs.last_hidden_state[:, -1:, :]`
- Loop-close (last agent → first agent) uses `outer_links[-1]` only when `r > 0`
- Inner loop loss: `1 - F.cosine_similarity(link(latent_h), target_emb, dim=-1).mean()`
- Outer loop optimizer covers `inner_links.parameters() + outer_links.parameters()` jointly
- For CPU/low-VRAM demo: use `torch_dtype=torch.float32`, `recursion_depth=1`, load one agent at a time

### Minimal requirements.txt

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

### Suggested demo config (`config.yaml`)

```yaml
agents:
  - model_name: Qwen/Qwen2.5-Math-1.5B
    role: Planner
  - model_name: meta-llama/Llama-3.2-1B
    role: Critic
  - model_name: google/gemma-2-2b
    role: Solver
recursion_depth: 3
hidden_dim: 4096        # RecursiveLink MLP hidden size
device: auto
dtype: bfloat16
checkpoint_dir: checkpoints/
```

---

## Commands reference (once code exists)

```bash
# One-time setup
pip install -r requirements.txt

# Run a single query (downloads models on first run)
python cli.py run "What is 15% of 240?"

# Train links on MATH500 subset (downloads dataset automatically)
python cli.py train --dataset math500

# Benchmark vs text-MAS baseline
python cli.py bench --dataset math500 --num-samples 50

# Debug: decode latent probes each round
python cli.py run "Solve for x: 2x + 5 = 13" --probe
```

---

## Key facts from the paper (avoid reimplementing wrong)

- Only ~13M trainable params across all links; `0.31%` of total system — if your link count is much larger, something is wrong
- RecursiveLink uses **residual + MLP**: `return residual(h) + mlp(h)` — not just MLP
- Inner loop warm-starts **per-link independently** before the outer joint pass
- Paper tests recursion depths 1–5; depth 3 is the sweet spot for the Sequential pattern
- Accuracy gain is ~8.3% on average; token reduction is 34–75%; both degrade if you decode intermediate latents
