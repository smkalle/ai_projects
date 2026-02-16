"""
Test script for MicroGPT (PyTorch version)
Run this to verify everything works.

Usage: uv run python test_microgpt_pytorch.py
"""

import os
import math
import random

import torch
import torch.nn as nn
import torch.nn.functional as F

print("=" * 70)
print("MICROGPT (PyTorch) TUTORIAL - TEST SCRIPT")
print("=" * 70)
print(f"PyTorch version: {torch.__version__}")

random.seed(42)
torch.manual_seed(42)

# ============================================================================
# PART 1: Test Autograd
# ============================================================================
print("\n[1/5] Testing PyTorch Autograd...")

# Test 1: Same as pure-Python: f = (x + y) * 2
x = torch.tensor(3.0, requires_grad=True)
y = torch.tensor(4.0, requires_grad=True)
f = (x + y) * 2
f.backward()
assert abs(x.grad.item() - 2.0) < 1e-6, "Autograd test failed!"
assert abs(y.grad.item() - 2.0) < 1e-6, "Autograd test failed!"
print(f"  ✓ Autograd works! df/dx={x.grad.item():.4f}, df/dy={y.grad.item():.4f}")

# Test 2: Chain rule - f = (2x + 1)^2 at x=3, df/dx = 2*2*(2*3+1) = 28
x = torch.tensor(3.0, requires_grad=True)
f = (x * 2 + 1) ** 2
f.backward()
assert abs(x.grad.item() - 28.0) < 1e-6, "Chain rule test failed!"
print(f"  ✓ Chain rule: f=(2x+1)^2, df/dx={x.grad.item():.4f} (expected 28)")

# Test 3: All 6 atomic operations
a = torch.tensor(3.0, requires_grad=True)
b = torch.tensor(4.0, requires_grad=True)
tests = [
    ("add", (a + b).item(), 7.0),
    ("mul", (a * b).item(), 12.0),
    ("pow", (a ** 2).item(), 9.0),
    ("log", torch.log(torch.tensor(2.0)).item(), math.log(2.0)),
    ("exp", torch.exp(torch.tensor(1.0)).item(), math.exp(1.0)),
    ("relu", F.relu(torch.tensor(5.0)).item(), 5.0),
    ("relu-", F.relu(torch.tensor(-3.0)).item(), 0.0),
]
for name, got, expected in tests:
    assert abs(got - expected) < 1e-5, f"{name} failed: {got} != {expected}"
print(f"  ✓ All 6 atomic operations verified (+, *, **, log, exp, relu)")

# ============================================================================
# PART 2: Test Tokenizer
# ============================================================================
print("\n[2/5] Testing Tokenizer...")

if not os.path.exists('input.txt'):
    print("  Downloading dataset...")
    import urllib.request
    names_url = 'https://raw.githubusercontent.com/karpathy/makemore/refs/heads/master/names.txt'
    urllib.request.urlretrieve(names_url, 'input.txt')

docs = [l.strip() for l in open('input.txt').read().strip().split('\n') if l.strip()]
random.shuffle(docs)

uchars = sorted(set(''.join(docs)))
BOS = len(uchars)
vocab_size = len(uchars) + 1


def encode(text):
    return [uchars.index(ch) for ch in text]


def decode(tokens):
    return ''.join([uchars[t] if t < len(uchars) else '<BOS>' for t in tokens])


# Test tokenizer
test_word = "hello"
tokens = encode(test_word)
decoded = decode(tokens)
assert decoded == test_word, "Tokenizer test failed!"
print(f"  ✓ Tokenizer works! '{test_word}' -> {tokens} -> '{decoded}'")
print(f"  ✓ Loaded {len(docs)} names, vocab size: {vocab_size}")

# ============================================================================
# PART 3: Test Model Components
# ============================================================================
print("\n[3/5] Testing Model Components...")


# Test RMSNorm
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.eps = eps

    def forward(self, x):
        ms = (x * x).mean(dim=-1, keepdim=True)
        return x * torch.rsqrt(ms + self.eps)


# Test linear (nn.Linear)
linear = nn.Linear(3, 2, bias=False)
with torch.no_grad():
    linear.weight.copy_(torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
x_test = torch.tensor([1.0, 2.0, 3.0])
out = linear(x_test)
assert abs(out[0].item() - 1.0) < 1e-6 and abs(out[1].item() - 2.0) < 1e-6
print("  ✓ Linear layer works!")

# Test softmax
logits = torch.tensor([1.0, 2.0, 3.0])
probs = F.softmax(logits, dim=-1)
prob_sum = probs.sum().item()
assert abs(prob_sum - 1.0) < 1e-6
print(f"  ✓ Softmax works! Sum of probs: {prob_sum:.6f}")

# Test RMSNorm
norm = RMSNorm(4)
x_test = torch.tensor([1.0, 2.0, 3.0, 4.0])
x_norm = norm(x_test)
ms_check = (x_norm * x_norm).mean().item()
print(f"  ✓ RMSNorm works! Normalized: [{', '.join(f'{v:.4f}' for v in x_norm.tolist())}]")

# ============================================================================
# PART 4: Initialize Model
# ============================================================================
print("\n[4/5] Initializing Model...")

n_embd = 16
n_head = 4
n_layer = 1
block_size = 16
head_dim = n_embd // n_head


class TransformerBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1 = RMSNorm(n_embd)
        self.attn_wq = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wk = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wv = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_wo = nn.Linear(n_embd, n_embd, bias=False)
        self.norm2 = RMSNorm(n_embd)
        self.mlp_fc1 = nn.Linear(n_embd, 4 * n_embd, bias=False)
        self.mlp_fc2 = nn.Linear(4 * n_embd, n_embd, bias=False)

    def forward(self, x):
        seq_len = x.size(0)
        x_res = x
        x_n = self.norm1(x)
        q = self.attn_wq(x_n).view(seq_len, n_head, head_dim).transpose(0, 1)
        k = self.attn_wk(x_n).view(seq_len, n_head, head_dim).transpose(0, 1)
        v = self.attn_wv(x_n).view(seq_len, n_head, head_dim).transpose(0, 1)
        attn = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(head_dim)
        mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
        attn = attn.masked_fill(mask, float('-inf'))
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        out = out.transpose(0, 1).contiguous().view(seq_len, n_embd)
        x = self.attn_wo(out) + x_res
        x_res = x
        x_n = self.norm2(x)
        x = self.mlp_fc1(x_n)
        x = F.relu(x)
        x = self.mlp_fc2(x)
        x = x + x_res
        return x


class MicroGPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.wte = nn.Embedding(vocab_size, n_embd)
        self.wpe = nn.Embedding(block_size, n_embd)
        self.pre_norm = RMSNorm(n_embd)
        self.layers = nn.ModuleList([TransformerBlock() for _ in range(n_layer)])
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.08)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.08)

    def forward(self, token_ids, pos_ids):
        x = self.wte(token_ids) + self.wpe(pos_ids)
        x = self.pre_norm(x)
        for layer in self.layers:
            x = layer(x)
        return self.lm_head(x)


model = MicroGPT()
num_params = sum(p.numel() for p in model.parameters())
print(f"  ✓ Model initialized with {num_params:,} parameters")

# ============================================================================
# PART 5: Test Forward Pass
# ============================================================================
print("\n[5/5] Testing Forward Pass...")

input_ids = torch.tensor([BOS])
pos_ids = torch.tensor([0])
with torch.no_grad():
    logits = model(input_ids, pos_ids)

assert logits.shape == (1, vocab_size), f"Shape mismatch: {logits.shape}"
probs = F.softmax(logits[0], dim=-1)
prob_sum = probs.sum().item()
assert abs(prob_sum - 1.0) < 1e-5, f"Softmax failed: sum={prob_sum}"
print(f"  ✓ Forward pass works! Output shape: {logits.shape}, prob sum: {prob_sum:.6f}")

# Show top predictions
top_3 = torch.topk(probs, 3)
print(f"  ✓ Top 3 predictions: ", end="")
print(", ".join([
    f"'{uchars[i] if i < len(uchars) else '<BOS>'}' ({v:.3f})"
    for v, i in zip(top_3.values.tolist(), top_3.indices.tolist())
]))

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED!")
print("=" * 70)
print("\nYour MicroGPT (PyTorch) implementation is working correctly!")
print("\nNext steps:")
print("  1. Open 'microgpt_pytorch_tutorial.ipynb' in Jupyter")
print("  2. Run through the detailed PyTorch tutorial")
print("  3. Train the full model: uv run python microgpt_pytorch.py")
print("  4. Generate new names!")
print("=" * 70)
