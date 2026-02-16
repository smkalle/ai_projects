"""
MicroGPT (PyTorch) - Training Script
Train a small GPT model and generate names using PyTorch.

This is the PyTorch equivalent of microgpt_simple.py. The architecture is
identical (~8,000 parameters), but PyTorch replaces our custom Value autograd
engine with optimized C++ tensor operations.

Usage:  uv run python microgpt_pytorch.py

Based on Andrej Karpathy's minimal GPT implementation.
"""

import os
import math
import random
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F

# ============================================================================
# 0. SETUP
# ============================================================================
random.seed(42)
torch.manual_seed(42)

# Automatic device selection: CUDA > MPS > CPU
device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

print("=" * 70)
print("MICROGPT (PyTorch) - Training a Minimal GPT")
print("=" * 70)
print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Device: {device} | PyTorch: {torch.__version__}\n")

# ============================================================================
# 1. AUTOGRAD - PyTorch's Built-in Automatic Differentiation
# ============================================================================
# In the pure-Python version, we built a Value class with 6 atomic operations
# (+, *, **, log, exp, relu) and a 30-line backward() method.
#
# PyTorch does the EXACT SAME THING -- topological sort + chain rule --
# but on tensors (batches of numbers) instead of scalars, using optimized
# C++/CUDA kernels. Same math, ~100x faster.
#
# Value(3.0)  -->  torch.tensor(3.0, requires_grad=True)
# f.backward() --> loss.backward()  (same algorithm)
print("[1/7] PyTorch autograd ready (built-in)")
print("  ✓ Same algorithm as our Value class, but on tensors")

# ============================================================================
# 2. DATASET & TOKENIZER
# ============================================================================
print("\n[2/7] Loading dataset and building tokenizer...")

if not os.path.exists('input.txt'):
    print("  Downloading names dataset...")
    import urllib.request
    names_url = 'https://raw.githubusercontent.com/karpathy/makemore/refs/heads/master/names.txt'
    urllib.request.urlretrieve(names_url, 'input.txt')

docs = [l.strip() for l in open('input.txt').read().strip().split('\n') if l.strip()]
random.shuffle(docs)
print(f"  ✓ Loaded {len(docs)} names")

uchars = sorted(set(''.join(docs)))
BOS = len(uchars)
vocab_size = len(uchars) + 1
print(f"  ✓ Vocabulary: {vocab_size} tokens ({len(uchars)} characters + BOS)")

# ============================================================================
# 3. MODEL COMPONENTS
# ============================================================================
# In pure Python we wrote standalone functions: linear(), softmax(), rmsnorm().
# In PyTorch these become nn.Module subclasses or built-in functions.
#
# Our linear()   -->  nn.Linear (same W @ x, but batched & optimized)
# Our softmax()  -->  F.softmax (same exp/sum, but numerically stable)
# Our rmsnorm()  -->  manual tensor ops (same x / sqrt(mean(x^2) + eps))
print("\n[3/7] Defining model components...")


class RMSNorm(nn.Module):
    """Root Mean Square normalization.

    Same as our pure-Python rmsnorm():
        scale = (mean(x^2) + eps) ^ -0.5
        return x * scale
    """
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.eps = eps

    def forward(self, x):
        ms = (x * x).mean(dim=-1, keepdim=True)
        return x * torch.rsqrt(ms + self.eps)


print("  ✓ RMSNorm, nn.Linear, F.softmax ready")

# ============================================================================
# 4. GPT MODEL
# ============================================================================
print("\n[4/7] Defining and initializing GPT model...")

# Same hyperparameters as the pure-Python version
n_embd = 16
n_head = 4
n_layer = 1
block_size = 16
head_dim = n_embd // n_head


class MicroGPT(nn.Module):
    """A minimal GPT model.

    Architecture (identical to pure-Python version):
        Token + Position Embedding -> RMSNorm
        -> Multi-Head Attention + Residual -> RMSNorm
        -> MLP (Linear->ReLU->Linear) + Residual
        -> Linear -> Logits

    ~8,000 parameters. 1 layer, 4 heads, 16-dim embeddings.
    """

    def __init__(self):
        super().__init__()
        # Embeddings
        self.wte = nn.Embedding(vocab_size, n_embd)   # token embeddings
        self.wpe = nn.Embedding(block_size, n_embd)    # position embeddings

        # Pre-norm (applied after embedding, same as pure-Python)
        self.pre_norm = RMSNorm(n_embd)

        # Transformer layers
        self.layers = nn.ModuleList([TransformerBlock() for _ in range(n_layer)])

        # Output head
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

        # Initialize weights with small std (same as pure-Python: std=0.08)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.08)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.08)

    def forward(self, token_ids, pos_ids):
        """Forward pass for a sequence of tokens.

        Args:
            token_ids: (seq_len,) token indices
            pos_ids:   (seq_len,) position indices

        Returns:
            logits: (seq_len, vocab_size) prediction scores
        """
        # Token + position embedding (same as pure-Python: tok_emb + pos_emb)
        x = self.wte(token_ids) + self.wpe(pos_ids)  # (seq_len, n_embd)

        # Pre-norm before transformer blocks (same as pure-Python)
        x = self.pre_norm(x)

        # Transformer blocks
        for layer in self.layers:
            x = layer(x)

        # Project to vocabulary (same as: logits = linear(x, lm_head))
        logits = self.lm_head(x)  # (seq_len, vocab_size)
        return logits


class TransformerBlock(nn.Module):
    """One transformer block: Attention + MLP, both with residual connections."""

    def __init__(self):
        super().__init__()
        # Attention
        self.norm1 = RMSNorm(n_embd)
        self.attn_wq = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wk = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wv = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wo = nn.Linear(n_embd, n_embd, bias=False)

        # MLP
        self.norm2 = RMSNorm(n_embd)
        self.mlp_fc1 = nn.Linear(n_embd, 4 * n_embd, bias=False)
        self.mlp_fc2 = nn.Linear(4 * n_embd, n_embd, bias=False)

    def forward(self, x):
        """
        Same structure as pure-Python:
            x_res = x
            x = rmsnorm(x)
            x = attention(x)  # Q*K^T/sqrt(d) -> softmax -> V
            x = x + x_res     # residual
            x_res = x
            x = rmsnorm(x)
            x = mlp(x)        # linear -> relu -> linear
            x = x + x_res     # residual
        """
        seq_len = x.size(0)

        # --- Attention block ---
        x_res = x
        x_norm = self.norm1(x)

        # Q, K, V projections (same as: q = linear(x, wq))
        q = self.attn_wq(x_norm)  # (seq_len, n_embd)
        k = self.attn_wk(x_norm)
        v = self.attn_wv(x_norm)

        # Reshape for multi-head: (seq_len, n_head, head_dim)
        q = q.view(seq_len, n_head, head_dim)
        k = k.view(seq_len, n_head, head_dim)
        v = v.view(seq_len, n_head, head_dim)

        # Attention scores: Q*K^T / sqrt(d) for each head
        # (n_head, seq_len, head_dim) @ (n_head, head_dim, seq_len)
        q = q.transpose(0, 1)  # (n_head, seq_len, head_dim)
        k = k.transpose(0, 1)
        v = v.transpose(0, 1)

        attn = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(head_dim)

        # Causal mask: each token can only attend to previous tokens
        # (same as pure-Python: we only loop over past keys)
        mask = torch.triu(torch.ones(seq_len, seq_len, device=x.device), diagonal=1).bool()
        attn = attn.masked_fill(mask, float('-inf'))

        # Softmax -> weighted sum of values
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)  # (n_head, seq_len, head_dim)

        # Concatenate heads and project
        out = out.transpose(0, 1).contiguous().view(seq_len, n_embd)
        x = self.attn_wo(out) + x_res  # residual connection

        # --- MLP block ---
        x_res = x
        x_norm = self.norm2(x)
        x = self.mlp_fc1(x_norm)
        x = F.relu(x)                 # same as: [xi.relu() for xi in x]
        x = self.mlp_fc2(x)
        x = x + x_res                 # residual connection

        return x


model = MicroGPT().to(device)
num_params = sum(p.numel() for p in model.parameters())
print(f"  ✓ Model: {num_params:,} parameters")
print(f"    - Embedding dim: {n_embd}")
print(f"    - Attention heads: {n_head}")
print(f"    - Layers: {n_layer}")
print(f"    - Context length: {block_size}")

# ============================================================================
# 5. TRAINING
# ============================================================================
print(f"\n[5/7] Training model...")

# Same optimizer settings as pure-Python version
learning_rate = 0.01
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, betas=(0.85, 0.99))

# Linear LR decay schedule (same as: lr_t = lr * (1 - step/num_steps))
num_steps = 1000
scheduler = torch.optim.lr_scheduler.LinearLR(
    optimizer, start_factor=1.0, end_factor=0.0, total_iters=num_steps
)

log_interval = 100
print(f"  Training for {num_steps} steps...\n")

loss_history = []
start_time = datetime.now()

model.train()
for step in range(num_steps):
    # Get training example (same as pure-Python: one name per step)
    doc = docs[step % len(docs)]
    tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
    n = min(block_size, len(tokens) - 1)

    # Convert to tensors
    input_ids = torch.tensor(tokens[:n], device=device)
    target_ids = torch.tensor(tokens[1:n + 1], device=device)
    pos_ids = torch.arange(n, device=device)

    # Forward pass
    logits = model(input_ids, pos_ids)  # (n, vocab_size)

    # Cross-entropy loss (same as: -log(softmax(logits)[target]))
    loss = F.cross_entropy(logits, target_ids)
    loss_history.append(loss.item())

    # Backward pass (same algorithm as our Value.backward())
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    scheduler.step()

    # Logging
    if (step + 1) % log_interval == 0:
        elapsed = (datetime.now() - start_time).total_seconds()
        avg_loss = sum(loss_history[max(0, step - log_interval + 1):step + 1]) / min(step + 1, log_interval)
        steps_per_sec = (step + 1) / elapsed
        print(f"  Step {step + 1:4d}/{num_steps} | Loss: {loss.item():.4f} | "
              f"Avg: {avg_loss:.4f} | Speed: {steps_per_sec:.1f} steps/sec")

elapsed = (datetime.now() - start_time).total_seconds()
print(f"\n  ✓ Training complete in {elapsed:.1f}s")
print(f"  ✓ Final loss: {loss_history[-1]:.4f}")
print(f"  ✓ Loss improved by {loss_history[0] - loss_history[-1]:.4f}")

# ============================================================================
# 6. GENERATION
# ============================================================================
print("\n[6/7] Generating new names...\n")


@torch.no_grad()
def generate(temperature=0.5):
    """Generate a new name by autoregressive sampling.

    Same logic as pure-Python:
        Start with BOS, predict next token, feed back, repeat until BOS.
    """
    model.eval()
    token_id = BOS
    chars = []

    for pos_id in range(block_size):
        input_t = torch.tensor([token_id], device=device)
        pos_t = torch.tensor([pos_id], device=device)

        logits = model(input_t, pos_t)  # (1, vocab_size)
        logits = logits[0] / temperature

        probs = F.softmax(logits, dim=-1)
        token_id = torch.multinomial(probs, 1).item()

        if token_id == BOS:
            break
        chars.append(uchars[token_id])

    model.train()
    return ''.join(chars)


# Generate samples
print("Generated names (temperature=0.5):\n")
for i in range(20):
    name = generate(temperature=0.5)
    print(f"  {i + 1:2d}. {name}")

# Try different temperatures
print("\n" + "=" * 70)
print("TEMPERATURE COMPARISON")
print("=" * 70)

for temp in [0.3, 0.7, 1.0]:
    print(f"\nTemperature = {temp} ({'conservative' if temp < 0.5 else 'balanced' if temp < 0.9 else 'creative'}):")
    names = [generate(temperature=temp) for _ in range(10)]
    print(f"  {', '.join(names)}")

# ============================================================================
# 7. SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✓ TRAINING AND GENERATION COMPLETE!")
print("=" * 70)
print(f"\nTraining statistics:")
print(f"  Initial loss: {loss_history[0]:.4f}")
print(f"  Final loss: {loss_history[-1]:.4f}")
print(f"  Improvement: {(loss_history[0] - loss_history[-1]) / loss_history[0] * 100:.1f}%")
print(f"  Training time: {elapsed:.1f}s")
print(f"  Steps per second: {num_steps / elapsed:.1f}")
print(f"\nModel info:")
print(f"  Parameters: {num_params:,}")
print(f"  Vocabulary size: {vocab_size}")
print(f"  Training examples: {len(docs):,}")
print(f"  Device: {device}")

print(f"\nComparison with pure-Python version:")
print(f"  Pure Python: ~1-2 steps/sec (scalar Value autograd)")
print(f"  PyTorch:     ~{num_steps / elapsed:.0f} steps/sec (tensor autograd)")
print(f"  Speedup:     Same math, vectorized operations")

print("\n" + "=" * 70)
print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
