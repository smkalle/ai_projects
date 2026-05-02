# Technical Specification — RecursiveMAS CLI Demo

**Paper**: arXiv:2604.25917  
**Pattern**: Sequential (Planner → Critic → Solver)  
**Target hardware**: Single 16 GB GPU (bfloat16) or CPU (float32, depth=1)

---

## 1. Goals

| Goal | Metric |
|------|--------|
| Demonstrate latent-space MAS | End-to-end `run` produces a decoded answer |
| Show token savings | `bench` reports token count vs text-MAS baseline |
| Train only link weights | Checkpoint size ≪ full model size |
| Runnable on consumer hardware | Works on 16 GB VRAM or CPU with `--cpu` flag |

Non-goals: production throughput, vLLM backend, frontier (70B+) models.

---

## 2. Repository Layout

```
recursivemas/
├── recursive_link.py   # RecursiveLink nn.Module
├── mas_system.py       # RecursiveMAS orchestrator
├── train.py            # inner_loop_train(), outer_loop_train()
├── infer.py            # load_mas(), run_query(), probe_latent()
├── cli.py              # typer app: run / train / bench
├── config.yaml         # default runtime config
├── requirements.txt
└── checkpoints/        # created at runtime; link weights only
```

---

## 3. Module Specifications

### 3.1 `recursive_link.py`

```
RecursiveLink(in_dim, out_dim=None, hidden_dim=4096)
```

**Architecture**: two-layer residual MLP.

```
residual = Linear(in_dim, out_dim)   # or Identity when in_dim == out_dim
mlp      = Linear(in_dim, hidden_dim) → GELU → Linear(hidden_dim, out_dim)
forward  = residual(h) + mlp(h)      # NOT mlp(h) alone — residual is mandatory
```

**Link instances and parameter counts**:

| Link | in_dim | out_dim | Approx params |
|------|--------|---------|---------------|
| `inner_links[0]` (Planner self) | 1536 | 1536 | ~25M... |

Wait — the paper claims ~13M total. With `hidden_dim=4096`:

```
params per link ≈ 2 × (in_dim × hidden_dim + hidden_dim × out_dim)
               + residual Linear params
```

Use `hidden_dim=512` in the default config for the SLM demo to stay near 13M total. The tutorial's `hidden_dim=4096` was written for larger models. Verify total by summing `sum(p.numel() for p in mas.inner_links.parameters()) + sum(p.numel() for p in mas.outer_links.parameters())` after construction.

**Invariants**:
- `forward` must return same dtype as input `h`
- No dropout (inference must be deterministic)
- Initialise MLP layers with `nn.init.xavier_uniform_`; residual Linear with `nn.init.eye_`-like scaling if dims match, else `xavier_uniform_`

---

### 3.2 `mas_system.py`

```python
class RecursiveMAS(nn.Module):
    agents:      list[dict]          # {model, tokenizer, role}
    inner_links: nn.ModuleList       # len == N agents
    outer_links: nn.ModuleList       # len == N agents
                                     # outer_links[i]: agent[i] → agent[i+1]
                                     # outer_links[-1]: agent[-1] → agent[0] (loop-close)
    recursion_depth: int
```

**Constructor sequence**:
1. Load each model with `AutoModelForCausalLM.from_pretrained(..., torch_dtype=dtype, device_map=device_map)`.
2. Freeze all base model parameters: `p.requires_grad = False` for every parameter.
3. Build `inner_links[i] = RecursiveLink(hidden_size_i, hidden_size_i)`.
4. Build `outer_links[i] = RecursiveLink(hidden_size_i, hidden_size_{(i+1) % N})` for all `i`.

**`forward(input_text, return_final_text=True)`**:

```
h = agent[0].model.model.embed_tokens(tokenize(input_text))  # [B, L, d0]

for r in 0..recursion_depth-1:
    for i in 0..N-1:
        if i == 0 and r > 0:
            h = outer_links[-1](h)         # loop-close: last→first
        elif i > 0:
            h = outer_links[i-1](h)        # cross-agent transfer

        outputs = agent[i].model.model(inputs_embeds=h, use_cache=False)
        h = outputs.last_hidden_state[:, -1:, :]   # [B, 1, d_i]
        h = inner_links[i](h)                       # self-refinement

if return_final_text:
    logits = agent[-1].model.lm_head(h)             # [B, 1, vocab]
    token_ids = logits.argmax(-1)                   # greedy decode
    return agent[-1].tokenizer.decode(token_ids[0])
return h   # latent tensor for training loss
```

**Critical constraints**:
- `use_cache=False` — non-negotiable; KV cache is incompatible with `inputs_embeds` across recursion rounds.
- Always slice `[:, -1:, :]` (keep seq dim = 1) so subsequent `inputs_embeds` has shape `[B, 1, d]`.
- Base model weights must never accumulate gradients — assert `not p.requires_grad` in a unit test.

---

### 3.3 `train.py`

#### Inner loop — per-link cosine warm-start

```python
def inner_loop_train(mas, dataset, epochs=3, lr=1e-4, batch_size=4):
    for i, link in enumerate(mas.inner_links):
        opt = AdamW(link.parameters(), lr=lr)
        for epoch in range(epochs):
            for batch in DataLoader(dataset, batch_size=batch_size):
                # Produce latent_h: run agent[i] forward on question text (no_grad)
                with torch.no_grad():
                    h = get_agent_latent(mas, i, batch["question"])   # [B, 1, d_i]
                # Target: embedding of ground-truth answer tokens
                target_emb = mas.agents[i]["model"].model.embed_tokens(
                    batch["answer_ids"].to(device)
                )[:, :1, :]                                            # [B, 1, d_i]
                loss = 1 - F.cosine_similarity(link(h), target_emb, dim=-1).mean()
                opt.zero_grad(); loss.backward(); opt.step()
            print(f"  inner link[{i}] epoch {epoch+1}: loss={loss.item():.4f}")
```

#### Outer loop — full system cross-entropy

```python
def outer_loop_train(mas, dataset, epochs=5, lr=5e-5, batch_size=2):
    params = list(mas.inner_links.parameters()) + list(mas.outer_links.parameters())
    opt = AdamW(params, lr=lr)
    for epoch in range(epochs):
        total_loss = 0
        for batch in DataLoader(dataset, batch_size=batch_size):
            final_latent = mas(batch["question"], return_final_text=False)  # [B, 1, d_N]
            logits = mas.agents[-1]["model"].lm_head(final_latent)          # [B, 1, vocab]
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                batch["answer_ids"].view(-1)
            )
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item()
        ckpt = f"checkpoints/links_epoch{epoch+1}.pt"
        torch.save({
            "inner_links": mas.inner_links.state_dict(),
            "outer_links":  mas.outer_links.state_dict(),
        }, ckpt)
        print(f"outer epoch {epoch+1}: loss={total_loss/len(dataset):.4f} → {ckpt}")
```

**Order is fixed**: inner loop MUST complete before outer loop starts.

#### Dataset helper

Use `datasets` library; load MATH500 (or a subset):

```python
from datasets import load_dataset
ds = load_dataset("lighteval/MATH", split="test[:500]")
# fields used: ds["problem"] → question, ds["solution"] → answer
```

---

### 3.4 `infer.py`

```python
def load_mas(config_path="config.yaml", checkpoint=None) -> RecursiveMAS
    # Reads config.yaml, constructs RecursiveMAS, optionally loads checkpoint

def run_query(mas, question: str, probe: bool = False) -> dict:
    # Returns {"answer": str, "tokens": int, "latency_ms": float}
    # If probe=True, also returns {"probes": list[str]} — decoded latent per round

def probe_latent(mas, h: torch.Tensor) -> str:
    # Greedy-decode h using agent[-1].lm_head + tokenizer
    # Used by run_query when probe=True

def text_mas_baseline(question: str, agent_configs: list) -> dict:
    # Sequential text-passing: each agent gets prior agent's decoded text as prompt
    # Returns same dict shape as run_query for apples-to-apples bench comparison
```

---

### 3.5 `cli.py`

```python
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

app = typer.Typer()
console = Console()
```

#### `run` sub-command

```
python cli.py run QUESTION [--config PATH] [--checkpoint PATH] [--probe] [--cpu]
```

Output format:
```
┌─ Round 1 ──────────────────────────┐
│ [Planner] processing latent...     │
│ [Critic]  processing latent...     │
│ [Solver]  processing latent...     │
└────────────────────────────────────┘
...
Answer: 1/3
Tokens decoded: 4  |  Latency: 312 ms
```

With `--probe`:
```
Round 1 / Planner probe: "the integral bounds suggest..."
Round 1 / Critic  probe: "checking boundary conditions..."
...
```

#### `train` sub-command

```
python cli.py train [--dataset math500] [--inner-epochs 3] [--outer-epochs 5]
                    [--batch-size 4] [--lr 1e-4] [--config PATH] [--cpu]
```

Prints per-epoch loss; saves to `checkpoints/`.

#### `bench` sub-command

```
python cli.py bench [--dataset math500] [--num-samples 50] [--config PATH]
                    [--checkpoint PATH] [--cpu]
```

Output table:

```
                 RecursiveMAS    Text-MAS Baseline
Accuracy             72.0%           63.8%
Avg tokens/query       8              47
Avg latency          410 ms          890 ms
```

---

## 4. Configuration Schema (`config.yaml`)

```yaml
agents:
  - model_name: Qwen/Qwen2.5-Math-1.5B
    role: Planner
  - model_name: meta-llama/Llama-3.2-1B
    role: Critic
  - model_name: google/gemma-2-2b
    role: Solver

recursion_depth: 3      # paper sweet spot; use 1 for CPU demo
hidden_dim: 512         # RecursiveLink MLP inner dim; use 512 for ~13M params with SLMs
device: auto            # "auto" | "cpu" | "cuda:0"
dtype: bfloat16         # "bfloat16" | "float32" (float32 required for CPU)
checkpoint_dir: checkpoints/
```

Loaded via `pyyaml`; CLI flags override config values.

---

## 5. Tensor Shape Contract

Every hand-off between modules must conform:

| Transition | Tensor `h` shape | dtype |
|------------|-----------------|-------|
| After `embed_tokens` (Agent 0 input) | `[B, L, 1536]` | matches model dtype |
| After each agent forward | `[B, 1, d_i]` | same |
| After inner_link | `[B, 1, d_i]` | same |
| After outer_link | `[B, 1, d_{i+1}]` | same |
| Into `lm_head` | `[B, 1, d_N]` | same |
| Logits out | `[B, 1, vocab_N]` | same |

`B=1` for inference. Batch dimension is kept for training compatibility.

---

## 6. Link Count and Parameter Budget

For the 3-agent SLM demo:

| Link | in→out | MLP params (hidden=512) | Residual params |
|------|--------|------------------------|-----------------|
| `inner_links[0]` | 1536→1536 | 2×(1536×512) ≈ 1.57M | Identity (0) |
| `inner_links[1]` | 2048→2048 | 2×(2048×512) ≈ 2.10M | Identity (0) |
| `inner_links[2]` | 2304→2304 | 2×(2304×512) ≈ 2.36M | Identity (0) |
| `outer_links[0]` | 1536→2048 | 1536×512+512×2048 ≈ 1.84M | 1536×2048 ≈ 3.15M |
| `outer_links[1]` | 2048→2304 | 2048×512+512×2304 ≈ 2.23M | 2048×2304 ≈ 4.72M |
| `outer_links[2]` | 2304→1536 | 2304×512+512×1536 ≈ 1.97M | 2304×1536 ≈ 3.54M |

**Total ≈ 23M params** with `hidden_dim=512`. The paper's 13M figure is for larger base models where outer-link residuals dominate differently, or a narrower hidden dim. The key check: trainable params should be `< 1%` of total frozen params.

---

## 7. Error Handling

| Condition | Behaviour |
|-----------|-----------|
| Model not cached, no internet | `huggingface_hub.utils.RepositoryNotFoundError` → print actionable message: "Run with network access to download models" |
| VRAM OOM | Catch `torch.cuda.OutOfMemoryError` → suggest `--cpu` or `recursion_depth=1` |
| Mismatched checkpoint dims | `load_state_dict` strict=True → fail fast with dimension mismatch message |
| Missing `config.yaml` | Default to hardcoded fallback config; warn user |
| `--probe` without checkpoint | Allowed; probes show untrained latents (useful for debugging setup) |

---

## 8. Testing Strategy

No test framework is mandated; use `pytest` for convenience.

| Test | What to assert |
|------|----------------|
| `test_recursive_link_shapes` | `forward(h)` output shape matches `out_dim` |
| `test_recursive_link_residual` | Output ≠ `mlp(h)` alone (residual adds non-zero contribution) |
| `test_mas_forward_smoke` | `RecursiveMAS.forward("1+1")` returns a non-empty string (with tiny mock models) |
| `test_no_base_grad` | All `agent["model"].parameters()` have `requires_grad=False` after construction |
| `test_latent_shape_contract` | Shape at each pipeline stage matches the table in §5 |
| `test_checkpoint_roundtrip` | Save + load link weights; assert state dict keys match |

Use `transformers` `AutoModelForCausalLM` with a tiny random config (2 layers, 64 hidden) for unit tests — avoid downloading real models in CI.

---

## 9. Performance Targets (Demo, not Production)

| Scenario | Target |
|----------|--------|
| `run` latency, GPU bfloat16, depth=3 | < 2 s per query |
| `run` latency, CPU float32, depth=1 | < 30 s per query |
| `train` inner loop, 500 samples, 3 epochs | < 10 min on single A100 |
| `bench` 50 samples | < 5 min on single A100 |
| Link checkpoint size | < 100 MB |

---

## 10. Implementation Order

1. `recursive_link.py` — standalone, no dependencies; write unit tests immediately.
2. `mas_system.py` — depends on `recursive_link`; smoke test with mock tiny models.
3. `infer.py` — depends on `mas_system`; test `run_query` end-to-end before training.
4. `train.py` — depends on `mas_system` + `infer`; verify inner loop loss decreases.
5. `cli.py` — wires everything together; test each sub-command independently.
6. `config.yaml` + `requirements.txt` — fill in last once all defaults are confirmed.

Do not implement `cli.py` before `infer.py` is verified working — the CLI is a thin wrapper, not a place to debug tensor shapes.
