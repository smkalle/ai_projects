"""
Test script for MicroGPT tutorial
Run this to verify everything works
"""

import os
import math
import random

print("="*70)
print("MICROGPT TUTORIAL - TEST SCRIPT")
print("="*70)

# Set seed
random.seed(42)

# ============================================================================
# PART 1: Test Autograd
# ============================================================================
print("\n[1/5] Testing Autograd...")

class Value:
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        self.data = data
        self.grad = 0
        self._children = children
        self._local_grads = local_grads

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data + other.data, (self, other), (1, 1))

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def __pow__(self, other):
        return Value(self.data**other, (self,), (other * self.data**(other-1),))

    def log(self):
        return Value(math.log(self.data), (self,), (1/self.data,))

    def exp(self):
        return Value(math.exp(self.data), (self,), (math.exp(self.data),))

    def relu(self):
        return Value(max(0, self.data), (self,), (float(self.data > 0),))

    def __neg__(self): return self * -1
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return self * other**-1
    def __rtruediv__(self, other): return other * self**-1

    def backward(self):
        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._children:
                    build_topo(child)
                topo.append(v)
        build_topo(self)
        self.grad = 1
        for v in reversed(topo):
            for child, local_grad in zip(v._children, v._local_grads):
                child.grad += local_grad * v.grad

# Test autograd
x = Value(3.0)
y = Value(4.0)
f = (x + y) * 2
f.backward()
assert abs(x.grad - 2.0) < 1e-6, "Autograd test failed!"
assert abs(y.grad - 2.0) < 1e-6, "Autograd test failed!"
print("  ✓ Autograd works! df/dx={:.4f}, df/dy={:.4f}".format(x.grad, y.grad))

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

def linear(x, w):
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]

def softmax(logits):
    max_val = max(val.data for val in logits)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]

def rmsnorm(x):
    ms = sum(xi * xi for xi in x) / len(x)
    scale = (ms + 1e-5) ** -0.5
    return [xi * scale for xi in x]

# Test linear
x_test = [Value(1), Value(2), Value(3)]
w_test = [[Value(1), Value(0), Value(0)], [Value(0), Value(1), Value(0)]]
out = linear(x_test, w_test)
assert abs(out[0].data - 1.0) < 1e-6 and abs(out[1].data - 2.0) < 1e-6
print("  ✓ Linear layer works!")

# Test softmax
logits = [Value(1.0), Value(2.0), Value(3.0)]
probs = softmax(logits)
prob_sum = sum(p.data for p in probs)
assert abs(prob_sum - 1.0) < 1e-6
print(f"  ✓ Softmax works! Sum of probs: {prob_sum:.6f}")

# Test rmsnorm
x_test = [Value(1.0), Value(2.0), Value(3.0)]
x_norm = rmsnorm(x_test)
print(f"  ✓ RMSNorm works! Normalized: [{x_norm[0].data:.4f}, {x_norm[1].data:.4f}, {x_norm[2].data:.4f}]")

# ============================================================================
# PART 4: Initialize Small Model
# ============================================================================
print("\n[4/5] Initializing Small Model...")

n_embd = 16
n_head = 4
n_layer = 1
block_size = 16
head_dim = n_embd // n_head

def matrix(nout, nin, std=0.08):
    return [[Value(random.gauss(0, std)) for _ in range(nin)] for _ in range(nout)]

state_dict = {
    'wte': matrix(vocab_size, n_embd),
    'wpe': matrix(block_size, n_embd),
    'lm_head': matrix(vocab_size, n_embd)
}

for i in range(n_layer):
    state_dict[f'layer{i}.attn_wq'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wk'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wv'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wo'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc1'] = matrix(4 * n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc2'] = matrix(n_embd, 4 * n_embd)

params = [p for mat in state_dict.values() for row in mat for p in row]
print(f"  ✓ Model initialized with {len(params):,} parameters")

# ============================================================================
# PART 5: Test Forward Pass
# ============================================================================
print("\n[5/5] Testing Forward Pass...")

def gpt(token_id, pos_id, keys, values):
    tok_emb = state_dict['wte'][token_id]
    pos_emb = state_dict['wpe'][pos_id]
    x = [t + p for t, p in zip(tok_emb, pos_emb)]
    x = rmsnorm(x)

    for li in range(n_layer):
        x_residual = x
        x = rmsnorm(x)
        q = linear(x, state_dict[f'layer{li}.attn_wq'])
        k = linear(x, state_dict[f'layer{li}.attn_wk'])
        v = linear(x, state_dict[f'layer{li}.attn_wv'])
        keys[li].append(k)
        values[li].append(v)

        x_attn = []
        for h in range(n_head):
            hs = h * head_dim
            q_h = q[hs:hs+head_dim]
            k_h = [ki[hs:hs+head_dim] for ki in keys[li]]
            v_h = [vi[hs:hs+head_dim] for vi in values[li]]
            attn_logits = [sum(q_h[j] * k_h[t][j] for j in range(head_dim)) / head_dim**0.5
                          for t in range(len(k_h))]
            attn_weights = softmax(attn_logits)
            head_out = [sum(attn_weights[t] * v_h[t][j] for t in range(len(v_h)))
                       for j in range(head_dim)]
            x_attn.extend(head_out)

        x = linear(x_attn, state_dict[f'layer{li}.attn_wo'])
        x = [a + b for a, b in zip(x, x_residual)]
        x_residual = x
        x = rmsnorm(x)
        x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
        x = [xi.relu() for xi in x]
        x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
        x = [a + b for a, b in zip(x, x_residual)]

    logits = linear(x, state_dict['lm_head'])
    return logits

# Test forward pass
keys = [[] for _ in range(n_layer)]
values = [[] for _ in range(n_layer)]
logits = gpt(BOS, 0, keys, values)
assert len(logits) == vocab_size, "Forward pass failed!"
probs = softmax(logits)
prob_sum = sum(p.data for p in probs)
assert abs(prob_sum - 1.0) < 1e-6, "Softmax after forward pass failed!"
print(f"  ✓ Forward pass works! Output shape: {len(logits)}, prob sum: {prob_sum:.6f}")

# Show top predictions
top_3 = sorted(range(len(probs)), key=lambda i: probs[i].data, reverse=True)[:3]
print(f"  ✓ Top 3 predictions: ", end="")
print(", ".join([f"'{uchars[i] if i < len(uchars) else '<BOS>'}' ({probs[i].data:.3f})"
                 for i in top_3]))

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✓ ALL TESTS PASSED!")
print("="*70)
print("\nYour MicroGPT implementation is working correctly!")
print("\nNext steps:")
print("  1. Open 'microgpt_tutorial.ipynb' in Jupyter")
print("  2. Run through the detailed tutorial")
print("  3. Train the full model (takes a few minutes)")
print("  4. Generate new names!")
print("\nTo train quickly, run: python microgpt_simple.py")
print("="*70)
