import os
import math
import random
from datetime import datetime

random.seed(42)

print("Imports: os, math, random, datetime")
print("No PyTorch, TensorFlow, NumPy, or any other library needed.")

# --- CELL BOUNDARY ---

class Value:
    """A scalar value with automatic differentiation.

    This is the ENTIRE autograd engine. Every number in the neural network
    is a Value. Math on Values builds a computation graph. Then .backward()
    walks that graph in reverse to compute gradients via the chain rule.
    """
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        self.data = data
        self.grad = 0
        self._children = children
        self._local_grads = local_grads

    def __repr__(self):
        return f"Value({self.data:.6f})"

    # --- THE 6 ATOMIC OPERATIONS ---

    def __add__(self, other):            # a + b    -> da=1, db=1
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data + other.data, (self, other), (1, 1))

    def __mul__(self, other):            # a * b    -> da=b, db=a
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def __pow__(self, other):            # a ** n   -> da = n * a^(n-1)
        return Value(self.data**other, (self,), (other * self.data**(other-1),))

    def log(self):                       # log(a)   -> da = 1/a
        return Value(math.log(self.data), (self,), (1/self.data,))

    def exp(self):                       # exp(a)   -> da = exp(a)
        return Value(math.exp(self.data), (self,), (math.exp(self.data),))

    def relu(self):                      # max(0,a) -> da = 1 if a>0 else 0
        return Value(max(0, self.data), (self,), (float(self.data > 0),))

    # --- DERIVED OPERATIONS (built from the 6 above) ---
    def __neg__(self): return self * -1
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return self * other**-1
    def __rtruediv__(self, other): return other * self**-1

    def backward(self):
        """Backpropagate gradients through the entire computation graph."""
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
        return len(topo)

print("Value class defined -- the complete autograd engine")
print("6 atomic ops: +, *, **, log, exp, relu")

# --- CELL BOUNDARY ---

print("=== Testing the 6 Atomic Operations ===\n")

a, b = Value(3.0), Value(4.0)
tests = [
    ("add",    (a + b).data,             3.0 + 4.0),
    ("mul",    (a * b).data,             3.0 * 4.0),
    ("pow",    (a ** 2).data,            3.0 ** 2),
    ("log",    Value(2.0).log().data,    math.log(2.0)),
    ("exp",    Value(1.0).exp().data,    math.exp(1.0)),
    ("relu+",  Value(5.0).relu().data,   5.0),
    ("relu-",  Value(-3.0).relu().data,  0.0),
]
all_pass = True
for name, got, expected in tests:
    ok = abs(got - expected) < 1e-10
    all_pass = all_pass and ok
    print(f"  {name:6s}: got {got:10.6f}  expected {expected:10.6f}  [{'PASS' if ok else 'FAIL'}]")

print("\n=== Derived Operations ===\n")
x = Value(6.0)
for name, got, expected in [("neg", (-x).data, -6.0), ("sub", (Value(10.0)-x).data, 4.0), ("div", (x/Value(3.0)).data, 2.0)]:
    ok = abs(got - expected) < 1e-10
    all_pass = all_pass and ok
    print(f"  {name:6s}: got {got:10.6f}  expected {expected:10.6f}  [{'PASS' if ok else 'FAIL'}]")

assert all_pass
print("\nAll forward tests passed.")

# --- CELL BOUNDARY ---

print("=== Gradient Tests ===")
print("Predict each gradient BEFORE reading the output!\n")

# Test 1: f = x + y
x, y = Value(3.0), Value(4.0); f = x + y; f.backward()
print(f"Test 1: f = x + y       df/dx = {x.grad} (rule: 1)  df/dy = {y.grad} (rule: 1)")
assert abs(x.grad - 1.0) < 1e-10

# Test 2: f = x * y
x, y = Value(3.0), Value(4.0); f = x * y; f.backward()
print(f"Test 2: f = x * y       df/dx = {x.grad} (rule: b=4)  df/dy = {y.grad} (rule: a=3)")
assert abs(x.grad - 4.0) < 1e-10

# Test 3: f = x^3
x = Value(2.0); f = x ** 3; f.backward()
print(f"Test 3: f = x^3         df/dx = {x.grad} (power rule: 3*2^2=12)")
assert abs(x.grad - 12.0) < 1e-10

# Test 4: CHAIN RULE
x = Value(3.0); f = (x * 2 + 1) ** 2; f.backward()
print(f"Test 4: f = (2x+1)^2    df/dx = {x.grad} (chain: 2*(2*3+1)*2 = 28)")
assert abs(x.grad - 28.0) < 1e-10

# Test 5: DEEP CHAIN
x = Value(1.0); f = (x.exp() + 1).log(); f.backward()
expected = math.exp(1) / (math.exp(1) + 1)
print(f"Test 5: f = log(exp(x)+1)  df/dx = {x.grad:.6f} (sigmoid = {expected:.6f})")
assert abs(x.grad - expected) < 1e-6

print("\nAll gradient tests passed!")

# --- CELL BOUNDARY ---

def check_gradients(build_fn, inputs, names=None, h=1e-5):
    """Verify autograd vs numerical finite differences."""
    if names is None: names = [f"x{i}" for i in range(len(inputs))]
    vals = [Value(x) for x in inputs]
    output = build_fn(vals); output.backward()
    auto_grads = [v.grad for v in vals]
    num_grads = []
    for i in range(len(inputs)):
        vp = [Value(x) for x in inputs]; vp[i].data += h
        vm = [Value(x) for x in inputs]; vm[i].data -= h
        num_grads.append((build_fn(vp).data - build_fn(vm).data) / (2*h))
    print(f"  {'Input':>8s}  {'Autograd':>12s}  {'Numerical':>12s}  {'Match':>6s}")
    print(f"  {'-'*44}")
    ok = True
    for nm, ag, ng in zip(names, auto_grads, num_grads):
        m = abs(ag - ng) < h * 100; ok = ok and m
        print(f"  {nm:>8s}  {ag:12.6f}  {ng:12.6f}  {'OK' if m else 'FAIL':>6s}")
    return ok

print("=== Numerical Gradient Verification ===\n")
print("Test 1: f(x,y) = x^2 * y + y^3")
ok1 = check_gradients(lambda v: v[0]**2 * v[1] + v[1]**3, [3.0, 2.0], ['x','y'])
print("\nTest 2: f(x) = relu(log(exp(x)+1) * x^2)  [all 6 ops]")
ok2 = check_gradients(lambda v: ((v[0].exp()+1).log() * v[0]**2).relu(), [1.5], ['x'])
print("\nTest 3: cross-entropy loss (the EXACT loss we train with)")
def xent(v):
    mx = max(vi.data for vi in v)
    exps = [(vi - mx).exp() for vi in v]
    return -(exps[0] / sum(exps)).log()
ok3 = check_gradients(xent, [1.0, 2.0, 3.0], ['a','b','c'])
assert ok1 and ok2 and ok3
print("\nAll numerical checks passed -- autograd is correct!")

# --- CELL BOUNDARY ---

def count_graph_nodes(v):
    """Count nodes in the computation graph."""
    visited = set(); ops = 0; leaves = 0
    def walk(node):
        nonlocal ops, leaves
        if node not in visited:
            visited.add(node)
            if node._children:
                ops += 1
                for c in node._children: walk(c)
            else: leaves += 1
    walk(v)
    return {'total': len(visited), 'ops': ops, 'leaves': leaves}

x, y = Value(3.0), Value(4.0)
f = (x + y) * (x - y)
s = count_graph_nodes(f)
print(f"f = (x+y)*(x-y) = {f.data}")
print(f"  Graph: {s['total']} nodes = {s['ops']} ops + {s['leaves']} leaves")

x = Value(2.0); f = (x**2 + x*3 + 1).log()
s = count_graph_nodes(f)
print(f"\nf = log(x^2 + 3x + 1) = {f.data:.6f}")
print(f"  Graph: {s['total']} nodes = {s['ops']} ops + {s['leaves']} leaves")
print(f"\nEvery node has a tracked derivative. backward() walks them all.")

# --- CELL BOUNDARY ---

if not os.path.exists('input.txt'):
    print("Downloading names dataset...")
    import urllib.request
    url = 'https://raw.githubusercontent.com/karpathy/makemore/refs/heads/master/names.txt'
    urllib.request.urlretrieve(url, 'input.txt')
docs = [l.strip() for l in open('input.txt').read().strip().split('\n') if l.strip()]
random.shuffle(docs)

uchars = sorted(set(''.join(docs)))
BOS = len(uchars)
vocab_size = len(uchars) + 1

def encode(text): return [uchars.index(ch) for ch in text]
def decode(tokens): return ''.join(uchars[t] if t < len(uchars) else '<BOS>' for t in tokens)

print(f"Dataset: {len(docs):,} names")
print(f"Vocabulary: {vocab_size} tokens = {len(uchars)} chars + BOS(={BOS})")
print(f"Sample: {docs[:8]}")
for name in ["alice", "bob", "zara"]:
    assert decode(encode(name)) == name
print("\nEncode/decode roundtrip verified.")

# --- CELL BOUNDARY ---

print("=== Training Sequence Examples ===\n")
for name in ["emma", "bob", "lily"]:
    tokens = [BOS] + encode(name) + [BOS]
    print(f"\'{name}\' -> {tokens}")
    for i in range(len(tokens)-1):
        ic = uchars[tokens[i]] if tokens[i] < len(uchars) else 'BOS'
        tc = uchars[tokens[i+1]] if tokens[i+1] < len(uchars) else 'BOS'
        print(f"    pos {i}: \'{ic}\' -> \'{tc}\'")
    print()

# --- CELL BOUNDARY ---

def linear(x, w):
    """Matrix-vector multiply. Built from multiply + add."""
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]

# Test
x_t = [Value(1.0), Value(2.0), Value(3.0)]
w_t = [[Value(1),Value(0),Value(0)], [Value(0),Value(1),Value(0)]]
out = linear(x_t, w_t)
assert out[0].data == 1.0 and out[1].data == 2.0
print("linear: identity test passed")

print("\nGradient check:")
def lin_fn(v):
    x = v[:3]; w = [[v[3],v[4],v[5]], [v[6],v[7],v[8]]]
    return sum(linear(x, w))
check_gradients(lin_fn, [1.,2.,3.,.5,.3,.1,.2,.4,.6],
                ['x0','x1','x2','w00','w01','w02','w10','w11','w12'])

x16 = [Value(0.)]*16; w16 = [[Value(0.)]*16 for _ in range(16)]
s = sum(linear(x16, w16)); st = count_graph_nodes(s)
print(f"\nlinear(16->16): {st['ops']} atomic ops")

# --- CELL BOUNDARY ---

def softmax(logits):
    """Logits -> probabilities (sum to 1)."""
    max_val = max(val.data for val in logits)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]

probs = softmax([Value(1.0), Value(2.0), Value(3.0)])
psum = sum(p.data for p in probs)
assert abs(psum - 1.0) < 1e-6
print(f"softmax([1,2,3]) = [{', '.join(f'{p.data:.4f}' for p in probs)}]  sum={psum:.6f}")

print("\nGradient check (-log softmax = cross-entropy):")
check_gradients(lambda v: -(softmax(v)[0]).log(), [1.,2.,3.], ['a','b','c'])

# --- CELL BOUNDARY ---

def rmsnorm(x):
    """Root Mean Square normalization."""
    ms = sum(xi * xi for xi in x) / len(x)
    scale = (ms + 1e-5) ** -0.5
    return [xi * scale for xi in x]

x_t = [Value(1.), Value(2.), Value(3.), Value(4.)]
x_n = rmsnorm(x_t)
ms = sum(v.data**2 for v in x_n) / len(x_n)
print(f"rmsnorm([1,2,3,4]) = [{', '.join(f'{v.data:.4f}' for v in x_n)}]")
print(f"  Mean of squares: {ms:.6f} (should be ~1.0)")

print("\nGradient check:")
check_gradients(lambda v: sum(rmsnorm(v)), [1.,2.,3.,4.], ['x0','x1','x2','x3'])

# --- CELL BOUNDARY ---

print("=== Atomic Operations per Component ===\n")
for label, fn in [
    ("linear(16->16)", lambda: sum(linear([Value(0.)]*16, [[Value(0.)]*16 for _ in range(16)]))),
    ("linear(16->64)", lambda: sum(linear([Value(0.)]*16, [[Value(0.)]*16 for _ in range(64)]))),
    ("softmax(27)",    lambda: sum(softmax([Value(.1*i) for i in range(27)]))),
    ("rmsnorm(16)",    lambda: sum(rmsnorm([Value(.1*i) for i in range(16)]))),
]:
    s = count_graph_nodes(fn())
    print(f"  {label:20s}: {s['ops']:5d} ops")
print(f"\nA full forward pass chains THOUSANDS of these together.")

# --- CELL BOUNDARY ---

n_embd = 16; n_head = 4; n_layer = 1; block_size = 16
head_dim = n_embd // n_head

def matrix(nout, nin, std=0.08):
    return [[Value(random.gauss(0, std)) for _ in range(nin)] for _ in range(nout)]

state_dict = {'wte': matrix(vocab_size, n_embd), 'wpe': matrix(block_size, n_embd),
              'lm_head': matrix(vocab_size, n_embd)}
for i in range(n_layer):
    state_dict[f'layer{i}.attn_wq'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wk'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wv'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wo'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc1'] = matrix(4*n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc2'] = matrix(n_embd, 4*n_embd)

params = [p for mat in state_dict.values() for row in mat for p in row]

print("=== Model Parameters ===\n")
total = 0
for name, mat in state_dict.items():
    r, c = len(mat), len(mat[0]); n = r*c; total += n
    print(f"  {name:25s}  {r:3d} x {c:3d} = {n:5d}")
print(f"  {'TOTAL':25s}           {total:5d}")

# --- CELL BOUNDARY ---

def gpt(token_id, pos_id, keys, values):
    """GPT forward pass for one token. Every op is atomic, tracked by autograd."""
    tok_emb = state_dict['wte'][token_id]
    pos_emb = state_dict['wpe'][pos_id]
    x = [t + p for t, p in zip(tok_emb, pos_emb)]
    x = rmsnorm(x)
    for li in range(n_layer):
        # Attention
        x_res = x; x = rmsnorm(x)
        q = linear(x, state_dict[f'layer{li}.attn_wq'])
        k = linear(x, state_dict[f'layer{li}.attn_wk'])
        v = linear(x, state_dict[f'layer{li}.attn_wv'])
        keys[li].append(k); values[li].append(v)
        x_attn = []
        for h in range(n_head):
            hs = h * head_dim
            q_h = q[hs:hs+head_dim]
            k_h = [ki[hs:hs+head_dim] for ki in keys[li]]
            v_h = [vi[hs:hs+head_dim] for vi in values[li]]
            al = [sum(q_h[j]*k_h[t][j] for j in range(head_dim))/head_dim**0.5
                  for t in range(len(k_h))]
            aw = softmax(al)
            x_attn.extend([sum(aw[t]*v_h[t][j] for t in range(len(v_h)))
                           for j in range(head_dim)])
        x = linear(x_attn, state_dict[f'layer{li}.attn_wo'])
        x = [a+b for a, b in zip(x, x_res)]
        # MLP
        x_res = x; x = rmsnorm(x)
        x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
        x = [xi.relu() for xi in x]
        x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
        x = [a+b for a, b in zip(x, x_res)]
    return linear(x, state_dict['lm_head'])

print(f"GPT defined: {n_layer} layer, {n_head} heads, {n_embd}-dim")

# --- CELL BOUNDARY ---

print("=== Forward Pass Test ===\n")
keys_t, values_t = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
logits = gpt(BOS, 0, keys_t, values_t)
probs = softmax(logits)
assert len(logits) == vocab_size
assert abs(sum(p.data for p in probs) - 1.0) < 1e-6

top5 = sorted(range(len(probs)), key=lambda i: probs[i].data, reverse=True)[:5]
print("Top 5 predictions (untrained = random):")
for r, idx in enumerate(top5, 1):
    ch = uchars[idx] if idx < len(uchars) else 'BOS'
    print(f"  {r}. \'{ch}\' = {probs[idx].data:.4f}")

st = count_graph_nodes(-probs[0].log())
print(f"\nComputation graph (1 token): {st['total']:,} nodes ({st['ops']:,} ops)")

# --- CELL BOUNDARY ---

print("=== Processing \'emma\' token by token ===\n")
tokens = [BOS] + encode("emma") + [BOS]; n = len(tokens)-1
keys_a, values_a = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
losses_a = []
for pos_id in range(n):
    tid, tgt = tokens[pos_id], tokens[pos_id+1]
    logits = gpt(tid, pos_id, keys_a, values_a)
    probs = softmax(logits); lt = -probs[tgt].log(); losses_a.append(lt)
    ic = uchars[tid] if tid<len(uchars) else 'BOS'
    tc = uchars[tgt] if tgt<len(uchars) else 'BOS'
    st = count_graph_nodes(lt)
    print(f"  pos {pos_id}: \'{ic}\'->\'{tc}\'  loss={lt.data:.4f}  graph={st['total']:,} nodes")
total_loss = (1/n) * sum(losses_a)
st = count_graph_nodes(total_loss)
print(f"\nTotal loss: {total_loss.data:.4f}")
print(f"Total graph: {st['total']:,} nodes ({st['ops']:,} ops)")
nn = total_loss.backward()
print(f"Backward traversed {nn:,} nodes")
print(f"Params with gradients: {sum(1 for p in params if p.grad!=0)}/{len(params)}")
for p in params: p.grad = 0

# --- CELL BOUNDARY ---

print("=== One Training Step (Detailed) ===\n")
doc = docs[0]
tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
n = min(block_size, len(tokens)-1)
print(f"Name: \'{doc}\'  ({n} predictions)\n")

# Forward
print("FORWARD:")
ks, vs = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
losses = []
for pos_id in range(n):
    tid, tgt = tokens[pos_id], tokens[pos_id+1]
    logits = gpt(tid, pos_id, ks, vs); probs = softmax(logits)
    lt = -probs[tgt].log(); losses.append(lt)
    ic = uchars[tid] if tid<len(uchars) else 'BOS'
    tc = uchars[tgt] if tgt<len(uchars) else 'BOS'
    top3 = sorted(range(len(probs)), key=lambda i: probs[i].data, reverse=True)[:3]
    t3 = " ".join(f"\'{uchars[i] if i<len(uchars) else 'BOS'}\':{probs[i].data:.2f}" for i in top3)
    print(f"  \'{ic}\'->\'{tc}\' loss={lt.data:.3f}  top3=[{t3}]  {'HIT' if tgt in top3 else ''}")
loss = (1/n)*sum(losses)
print(f"  Avg loss: {loss.data:.4f}\n")

# Backward
print("BACKWARD:")
nn = loss.backward()
grads = [abs(p.grad) for p in params if p.grad!=0]
print(f"  {nn:,} nodes traversed")
print(f"  {len(grads)}/{len(params)} params got gradients")
if grads: print(f"  |grad| range: [{min(grads):.6f}, {max(grads):.6f}]\n")

# Adam demo
print("ADAM UPDATE (example: param[0]):")
p0 = params[0]; old = p0.data
mh = (0.15*p0.grad)/(1-0.85); vh = (0.01*p0.grad**2)/(1-0.99)
upd = 0.01*mh/(vh**0.5+1e-8)
print(f"  grad={p0.grad:.6f} -> update={upd:.6f}")
print(f"  {old:.6f} -> {old-upd:.6f}")
for p in params: p.grad = 0

# --- CELL BOUNDARY ---

learning_rate = 0.01; beta1, beta2, eps_adam = 0.85, 0.99, 1e-8
m = [0.0]*len(params); v = [0.0]*len(params)
num_steps = 1000; loss_history = []

print(f"Training {num_steps} steps on {len(docs):,} names...\n")
start_time = datetime.now()

for step in range(num_steps):
    doc = docs[step % len(docs)]
    tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
    n = min(block_size, len(tokens)-1)
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    losses = []
    for pos_id in range(n):
        token_id, target_id = tokens[pos_id], tokens[pos_id+1]
        logits = gpt(token_id, pos_id, keys, values)
        probs = softmax(logits)
        losses.append(-probs[target_id].log())
    loss = (1/n)*sum(losses); loss_history.append(loss.data)
    loss.backward()
    lr_t = learning_rate * (1 - step/num_steps)
    for i, p in enumerate(params):
        m[i] = beta1*m[i] + (1-beta1)*p.grad
        v[i] = beta2*v[i] + (1-beta2)*p.grad**2
        m_hat = m[i]/(1-beta1**(step+1)); v_hat = v[i]/(1-beta2**(step+1))
        p.data -= lr_t * m_hat / (v_hat**0.5 + eps_adam)
        p.grad = 0
    if (step+1) % 100 == 0 or step == 0:
        elapsed = (datetime.now()-start_time).total_seconds()
        avg = sum(loss_history[max(0,step-99):step+1])/min(step+1,100)
        print(f"  step {step+1:4d}/{num_steps} | loss {loss.data:.4f} | avg {avg:.4f} | "
              f"lr {lr_t:.4f} | {(step+1)/elapsed:.1f} s/s | \'{doc}\'")

elapsed = (datetime.now()-start_time).total_seconds()
print(f"\nDone in {elapsed:.0f}s. Final loss: {loss_history[-1]:.4f}")

# --- CELL BOUNDARY ---

print("=== Training Analysis ===\n")
for s, e in [(0,100),(100,300),(300,500),(500,700),(700,900),(900,1000)]:
    avg = sum(loss_history[s:e])/(e-s)
    print(f"  Steps {s+1:4d}-{e:4d}: {avg:.4f}  {'#'*int(avg*10)}")
imp = (loss_history[0]-loss_history[-1])/loss_history[0]*100
ppl = math.exp(sum(loss_history[-100:])/100)
print(f"\nImprovement: {loss_history[0]:.4f} -> {loss_history[-1]:.4f} ({imp:.1f}%)")
print(f"Final perplexity: {ppl:.1f} (random={vocab_size}, lower=better)")
print(f"Model is {vocab_size/ppl:.1f}x better than random guessing")

# --- CELL BOUNDARY ---

def generate(temperature=0.5):
    """Generate a name by sampling from the trained model."""
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    token_id = BOS; chars = []
    for pos_id in range(block_size):
        logits = gpt(token_id, pos_id, keys, values)
        probs = softmax([l/temperature for l in logits])
        token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
        if token_id == BOS: break
        chars.append(uchars[token_id])
    return ''.join(chars)

print("generate() defined")

# --- CELL BOUNDARY ---

print("=== Step-by-step Generation ===\n")
for si in range(3):
    kg, vg = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    tid = BOS; chars = []
    print(f"Sample {si+1}:")
    for pos_id in range(block_size):
        logits = gpt(tid, pos_id, kg, vg)
        probs = softmax([l/0.5 for l in logits])
        top3 = sorted(range(len(probs)), key=lambda i: probs[i].data, reverse=True)[:3]
        t3 = " ".join(f"\'{uchars[i] if i<len(uchars) else 'BOS'}\':{probs[i].data:.2f}" for i in top3)
        tid = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
        if tid == BOS:
            print(f"  pos {pos_id}: [{t3}] -> BOS (done)"); break
        chars.append(uchars[tid])
        print(f"  pos {pos_id}: [{t3}] -> \'{uchars[tid]}\'")
    print(f"  Result: \'{''.join(chars)}\'\n")

# --- CELL BOUNDARY ---

print("=== Temperature Comparison ===\n")
for temp in [0.3, 0.5, 0.8, 1.0, 1.5]:
    names = [generate(temp) for _ in range(10)]
    label = {0.3:"conservative",0.5:"balanced",0.8:"exploratory",1.0:"creative",1.5:"wild"}[temp]
    print(f"  temp={temp} ({label:12s}): {', '.join(names)}")

print(f"\n{'='*60}")
print(f"  20 Generated Names (temperature=0.5)")
print(f"{'='*60}\n")
gen = []
for i in range(20):
    name = generate(0.5); gen.append(name); print(f"  {i+1:2d}. {name}")
print(f"\nUnique: {len(set(gen))}/20  Avg len: {sum(len(n) for n in gen)/len(gen):.1f}")

# --- CELL BOUNDARY ---

print("=== Model: Real Names vs Nonsense ===\n")
for name in ["emma","liam","olivia","noah","ava","zzzzz","qqqq","aeiou","xyzw"]:
    tokens = [BOS]+encode(name)+[BOS]; n = len(tokens)-1
    kt, vt = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    total = 0.
    for pos_id in range(n):
        logits = gpt(tokens[pos_id], pos_id, kt, vt)
        probs = softmax(logits)
        total += -probs[tokens[pos_id+1]].log().data
    avg = total/n; ppl = math.exp(avg)
    print(f"  \'{name:8s}\': loss={avg:.3f}  ppl={ppl:6.1f}  {'#'*min(40,int(avg*8))}")
print(f"\nReal names have lower loss than nonsense.")

# --- CELL BOUNDARY ---

print("=== Attention Patterns (\'{}\'): ===\n".format("sarah"))
name = "sarah"; tokens_v = [BOS]+encode(name); chars_v = ['BOS']+list(name)
kv, vv = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
all_attn = []
for pos_id in range(len(tokens_v)):
    tid = tokens_v[pos_id]
    x = [t+p for t,p in zip(state_dict['wte'][tid], state_dict['wpe'][pos_id])]
    x = rmsnorm(x); li = 0; x = rmsnorm(x)
    q = linear(x, state_dict[f'layer{li}.attn_wq'])
    k = linear(x, state_dict[f'layer{li}.attn_wk'])
    kv[li].append(k); vv[li].append(linear(x, state_dict[f'layer{li}.attn_wv']))
    pa = []
    for h in range(n_head):
        hs = h*head_dim; q_h = q[hs:hs+head_dim]
        k_h = [ki[hs:hs+head_dim] for ki in kv[li]]
        al = [sum(q_h[j]*k_h[t][j] for j in range(head_dim))/head_dim**0.5
              for t in range(len(k_h))]
        pa.append([w.data for w in softmax(al)])
    all_attn.append(pa)
for h in range(n_head):
    print(f"Head {h}:")
    print("       "+"".join(f"{c:>7s}" for c in chars_v))
    for pi in range(len(tokens_v)):
        row = f"  {chars_v[pi]:>4s}: "
        for t in range(pi+1):
            w = all_attn[pi][h][t]
            if w > 0.3: row += f" [{w:.2f}]"
            elif w > 0.1: row += f"  {w:.2f} "
            else: row += f"  .    "
        print(row)
    print()

# --- CELL BOUNDARY ---

print("=== Gradient Flow by Layer ===\n")
doc = docs[0]
tokens = [BOS]+[uchars.index(ch) for ch in doc]+[BOS]; n = min(block_size, len(tokens)-1)
kg, vg = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
losses = []
for pos_id in range(n):
    logits = gpt(tokens[pos_id], pos_id, kg, vg)
    probs = softmax(logits); losses.append(-probs[tokens[pos_id+1]].log())
loss = (1/n)*sum(losses); loss.backward()
for name, mat in state_dict.items():
    g = [abs(p.grad) for row in mat for p in row]
    mg = sum(g)/len(g); mx = max(g)
    print(f"  {name:25s}: mean|g|={mg:.6f}  max={mx:.6f}  {'#'*min(30,int(mg*500))}")
for p in params: p.grad = 0
print(f"\nLarger gradients = more learning in that component")

# --- CELL BOUNDARY ---

x = Value(2.0); f = x**2 + x*3 + 1; f.backward()
print(f"f(2) = {f.data} (expected 11)  df/dx = {x.grad} (expected 7)")

# --- CELL BOUNDARY ---

tokens = [BOS]+encode("emma")+[BOS]; n = len(tokens)-1
kc, vc = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
lc = []
for pos_id in range(n):
    logits = gpt(tokens[pos_id], pos_id, kc, vc)
    probs = softmax(logits); lc.append(-probs[tokens[pos_id+1]].log())
st = count_graph_nodes((1/n)*sum(lc))
print(f"'emma' ({n} predictions): {st['total']:,} graph nodes, {st['ops']:,} operations")
print(f"Over {num_steps} training steps: ~{st['ops']*num_steps:,} total ops")
print(f"All differentiated by our 30-line autograd engine!")