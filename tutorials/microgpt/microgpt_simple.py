"""
MicroGPT - Simplified Training Script
Train a small GPT model and generate names

Based on Andrej Karpathy's minimal GPT implementation
"""

import os
import math
import random
from datetime import datetime

random.seed(42)

print("="*70)
print("MICROGPT - Training a Minimal GPT from Scratch")
print("="*70)
print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1. AUTOGRAD - Automatic Differentiation
# ============================================================================
print("[1/7] Building Autograd engine...")

class Value:
    """A scalar value with automatic differentiation."""
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
        """Backpropagate gradients."""
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

print("  ✓ Autograd ready")

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
print("\n[3/7] Defining model components...")

def linear(x, w):
    """Linear transformation: w @ x"""
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]

def softmax(logits):
    """Convert logits to probabilities."""
    max_val = max(val.data for val in logits)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]

def rmsnorm(x):
    """Root Mean Square normalization."""
    ms = sum(xi * xi for xi in x) / len(x)
    scale = (ms + 1e-5) ** -0.5
    return [xi * scale for xi in x]

print("  ✓ Linear, Softmax, RMSNorm ready")

# ============================================================================
# 4. INITIALIZE MODEL
# ============================================================================
print("\n[4/7] Initializing model parameters...")

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
print(f"  ✓ Model: {len(params):,} parameters")
print(f"    - Embedding dim: {n_embd}")
print(f"    - Attention heads: {n_head}")
print(f"    - Layers: {n_layer}")
print(f"    - Context length: {block_size}")

# ============================================================================
# 5. GPT MODEL
# ============================================================================
print("\n[5/7] Defining GPT architecture...")

def gpt(token_id, pos_id, keys, values):
    """GPT forward pass for a single token."""
    tok_emb = state_dict['wte'][token_id]
    pos_emb = state_dict['wpe'][pos_id]
    x = [t + p for t, p in zip(tok_emb, pos_emb)]
    x = rmsnorm(x)

    for li in range(n_layer):
        # Attention block
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

        # MLP block
        x_residual = x
        x = rmsnorm(x)
        x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
        x = [xi.relu() for xi in x]
        x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
        x = [a + b for a, b in zip(x, x_residual)]

    logits = linear(x, state_dict['lm_head'])
    return logits

print("  ✓ GPT model ready")

# ============================================================================
# 6. TRAINING
# ============================================================================
print("\n[6/7] Training model...")

learning_rate = 0.01
beta1, beta2, eps_adam = 0.85, 0.99, 1e-8
m = [0.0] * len(params)
v = [0.0] * len(params)

num_steps = 1000
log_interval = 100

print(f"  Training for {num_steps} steps...\n")

loss_history = []
start_time = datetime.now()

for step in range(num_steps):
    # Get training example
    doc = docs[step % len(docs)]
    tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
    n = min(block_size, len(tokens) - 1)

    # Forward pass
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    losses = []
    for pos_id in range(n):
        token_id, target_id = tokens[pos_id], tokens[pos_id + 1]
        logits = gpt(token_id, pos_id, keys, values)
        probs = softmax(logits)
        loss_t = -probs[target_id].log()
        losses.append(loss_t)

    loss = (1 / n) * sum(losses)
    loss_history.append(loss.data)

    # Backward pass
    loss.backward()

    # Adam update
    lr_t = learning_rate * (1 - step / num_steps)
    for i, p in enumerate(params):
        m[i] = beta1 * m[i] + (1 - beta1) * p.grad
        v[i] = beta2 * v[i] + (1 - beta2) * p.grad ** 2
        m_hat = m[i] / (1 - beta1 ** (step + 1))
        v_hat = v[i] / (1 - beta2 ** (step + 1))
        p.data -= lr_t * m_hat / (v_hat ** 0.5 + eps_adam)
        p.grad = 0

    # Logging
    if (step + 1) % log_interval == 0:
        elapsed = (datetime.now() - start_time).total_seconds()
        avg_loss = sum(loss_history[max(0, step-log_interval+1):step+1]) / min(step+1, log_interval)
        steps_per_sec = (step + 1) / elapsed
        print(f"  Step {step+1:4d}/{num_steps} | Loss: {loss.data:.4f} | "
              f"Avg: {avg_loss:.4f} | Speed: {steps_per_sec:.1f} steps/sec")

elapsed = (datetime.now() - start_time).total_seconds()
print(f"\n  ✓ Training complete in {elapsed:.1f}s")
print(f"  ✓ Final loss: {loss_history[-1]:.4f}")
print(f"  ✓ Loss improved by {loss_history[0] - loss_history[-1]:.4f}")

# ============================================================================
# 7. GENERATION
# ============================================================================
print("\n[7/7] Generating new names...\n")

def generate(temperature=0.5):
    """Generate a new name."""
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    token_id = BOS
    sample = []

    for pos_id in range(block_size):
        logits = gpt(token_id, pos_id, keys, values)
        probs = softmax([l / temperature for l in logits])
        token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
        if token_id == BOS:
            break
        sample.append(uchars[token_id])

    return ''.join(sample)

# Generate samples
print("Generated names (temperature=0.5):\n")
for i in range(20):
    name = generate(temperature=0.5)
    print(f"  {i+1:2d}. {name}")

# Try different temperatures
print("\n" + "="*70)
print("TEMPERATURE COMPARISON")
print("="*70)

for temp in [0.3, 0.7, 1.0]:
    print(f"\nTemperature = {temp} ({'conservative' if temp < 0.5 else 'balanced' if temp < 0.9 else 'creative'}):")
    names = [generate(temperature=temp) for _ in range(10)]
    print(f"  {', '.join(names)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✓ TRAINING AND GENERATION COMPLETE!")
print("="*70)
print(f"\nTraining statistics:")
print(f"  Initial loss: {loss_history[0]:.4f}")
print(f"  Final loss: {loss_history[-1]:.4f}")
print(f"  Improvement: {(loss_history[0] - loss_history[-1]) / loss_history[0] * 100:.1f}%")
print(f"  Training time: {elapsed:.1f}s")
print(f"  Steps per second: {num_steps / elapsed:.1f}")
print(f"\nModel info:")
print(f"  Parameters: {len(params):,}")
print(f"  Vocabulary size: {vocab_size}")
print(f"  Training examples: {len(docs):,}")

print("\n" + "="*70)
print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
