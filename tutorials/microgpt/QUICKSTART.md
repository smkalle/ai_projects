# MicroGPT Quick Start Guide

## 🎯 3 Ways to Use This Tutorial

### 1️⃣ Quick Test (1 minute)
Verify everything works without training:
```bash
python test_microgpt.py
```

**What it does:**
- Tests autograd system
- Tests tokenizer
- Tests model components
- Tests forward pass
- No training, just verification

### 2️⃣ Full Training (5-10 minutes)
Train the model and generate names:
```bash
python microgpt_simple.py
```

**What it does:**
- Trains for 1,000 steps
- Generates 20 new names
- Shows loss progression
- Tests different temperatures

**Expected output:**
```
Generated names (temperature=0.5):
  1. aria
  2. leon
  3. maya
  ...
```

### 3️⃣ Interactive Tutorial (30-60 minutes)
Step-by-step learning with detailed explanations:
```bash
jupyter notebook microgpt_tutorial.ipynb
```

**What it includes:**
- 10 detailed sections
- Tests after each component
- Visualizations and logging
- Experiments and analysis

---

## 📊 What Gets Built

### Model Architecture
```
Input: Character sequence
  ↓
Token Embedding (27 → 16)
  + Position Embedding
  ↓
RMSNorm
  ↓
Multi-Head Attention (4 heads)
  ↓
+ Residual Connection
  ↓
RMSNorm
  ↓
MLP (16 → 64 → 16, ReLU)
  ↓
+ Residual Connection
  ↓
Linear Projection (16 → 27)
  ↓
Softmax
  ↓
Output: Next character probabilities
```

### Model Size
- **Parameters**: ~8,000
- **Embedding dim**: 16
- **Attention heads**: 4
- **Layers**: 1
- **Context length**: 16 characters
- **Vocabulary**: 27 tokens (26 letters + BOS)

---

## 🧠 Key Concepts Explained Simply

### Autograd (Automatic Differentiation)
Think of it as: **Tracking how each number affects the final answer**

Example:
```python
x = Value(3)
y = x * 2  # y = 6
y.backward()  # Compute: how much does changing x affect y?
print(x.grad)  # Answer: 2 (doubling x doubles y)
```

### Tokenization
Think of it as: **Converting text to numbers**

Example:
```python
"hi" → [7, 8]  # Each character gets a number
[7, 8] → "hi"  # Can convert back
```

### Embeddings
Think of it as: **Representing each character as a vector of numbers**

Example:
```
'a' → [0.2, -0.5, 0.8, ...]  # 16 numbers
Position 0 → [0.1, 0.3, -0.2, ...]  # 16 numbers
Combined → [0.3, -0.2, 0.6, ...]  # Added together
```

### Self-Attention
Think of it as: **Each character looking at previous characters**

Example when processing 'hello':
```
'h' looks at: []           (nothing before)
'e' looks at: ['h']        (sees 'h')
'l' looks at: ['h', 'e']   (sees 'h' and 'e')
'l' looks at: ['h', 'e', 'l']
'o' looks at: ['h', 'e', 'l', 'l']
```

### Multi-Head Attention
Think of it as: **Looking at previous characters in multiple ways**

Example:
- **Head 1**: Looks for vowels
- **Head 2**: Looks for consonants
- **Head 3**: Looks for position patterns
- **Head 4**: Looks for frequency patterns

### Temperature in Generation
Think of it as: **Creativity dial**

Example:
```python
Temperature = 0.1  # Conservative, picks most likely character
  → "anna", "emma", "john"

Temperature = 0.5  # Balanced (default)
  → "aria", "leon", "kira"

Temperature = 1.5  # Creative, more random
  → "zylox", "qaira", "vynn"
```

---

## 🔍 Understanding the Code

### Minimal Example: Forward Pass

```python
# 1. Convert character to number
token_id = 0  # 'a'
pos_id = 0    # position 0

# 2. Get embeddings
tok_emb = state_dict['wte'][token_id]  # [16 numbers]
pos_emb = state_dict['wpe'][pos_id]    # [16 numbers]
x = [t + p for t, p in zip(tok_emb, pos_emb)]

# 3. Attention: look at previous tokens
q = linear(x, W_query)   # "What am I looking for?"
k = linear(x, W_key)     # "What do I contain?"
v = linear(x, W_value)   # "What do I communicate?"

# 4. MLP: process information
x = linear(x, W1)
x = [relu(xi) for xi in x]
x = linear(x, W2)

# 5. Predict next character
logits = linear(x, W_out)  # [27 numbers]
probs = softmax(logits)    # Convert to probabilities
```

### Minimal Example: Training Step

```python
# 1. Get training example
name = "alice"
tokens = [BOS, 'a', 'l', 'i', 'c', 'e', BOS]

# 2. Forward: predict each next character
for i in range(len(tokens) - 1):
    input_char = tokens[i]      # 'a'
    target_char = tokens[i + 1] # 'l'

    predictions = gpt(input_char, i, ...)
    loss = -log(predictions[target_char])  # How wrong were we?

# 3. Backward: compute gradients
loss.backward()  # How to adjust each parameter?

# 4. Update: improve parameters
for param in parameters:
    param.data -= learning_rate * param.grad
```

---

## 📈 Expected Training Progress

```
Step    100 | Loss: 3.2 → Model is learning basic patterns
Step    300 | Loss: 2.5 → Model understands common characters
Step    500 | Loss: 2.2 → Model captures character combinations
Step    800 | Loss: 2.0 → Model generates plausible names
Step   1000 | Loss: 1.9 → Model is reasonably trained
```

---

## 🎓 Learning Path

### Beginner (1-2 hours)
1. ✅ Run `test_microgpt.py` to see it works
2. ✅ Run `microgpt_simple.py` to see training
3. ✅ Read README.md for overview
4. ✅ Open tutorial notebook, read Part 1-3

### Intermediate (3-5 hours)
1. ✅ Complete full tutorial notebook
2. ✅ Understand each code block
3. ✅ Run experiments (Part 10)
4. ✅ Modify hyperparameters

### Advanced (1-2 days)
1. ✅ Implement from scratch without looking
2. ✅ Add new features (LayerNorm, GeLU, etc.)
3. ✅ Train on different datasets
4. ✅ Visualize attention patterns
5. ✅ Compare with PyTorch implementation

---

## 💡 Tips for Success

### 1. Start Simple
Don't try to understand everything at once. Focus on one concept at a time:
- Day 1: Autograd
- Day 2: Tokenization & Embeddings
- Day 3: Attention
- Day 4: Full model
- Day 5: Training & Generation

### 2. Run Code Frequently
Don't just read - run each code block and observe outputs:
```python
# Always print intermediate results
print(f"Shape: {len(x)}")
print(f"First few values: {[xi.data for xi in x[:5]]}")
```

### 3. Visualize
Draw diagrams of:
- Computation graphs for autograd
- Attention patterns
- Data flow through the model

### 4. Compare with Math
Match code to mathematical notation:
```python
# Code
out = sum(qi * ki for qi, ki in zip(q, k))

# Math
out = q · k = Σ(qi × ki)
```

### 5. Experiment
Change things and see what happens:
- What if learning_rate = 0.1? (too high)
- What if n_embd = 4? (too small)
- What if temperature = 2.0? (too random)

---

## 🐛 Common Issues

### Issue: "NameError: name 'Value' is not defined"
**Solution**: Make sure you run cells in order from top to bottom.

### Issue: Generated names are gibberish
**Solution**: Train longer (increase `num_steps` to 2000-5000).

### Issue: Loss is not decreasing
**Solutions**:
- Check learning rate (try 0.001 or 0.1)
- Ensure backward() is called
- Verify gradients are not zero

### Issue: Code is slow
**Expected**: Pure Python is slow! This is for learning, not production.
- 1-2 steps/second is normal
- For speed, use PyTorch/TensorFlow

---

## 📚 What to Study Next

### Immediate Next Steps
1. **PyTorch Implementation** - See how to do this 100x faster
2. **Larger Models** - Scale to GPT-2 size
3. **Different Tasks** - Apply to text classification, summarization

### Deeper Understanding
1. **Attention Mechanisms** - Multi-query, Flash Attention
2. **Training Techniques** - Mixed precision, gradient clipping
3. **Architecture Variants** - BERT, T5, LLaMA

### Production Skills
1. **Optimization** - Quantization, pruning, distillation
2. **Deployment** - ONNX, TensorRT, serving at scale
3. **Fine-tuning** - LoRA, QLoRA, instruction tuning

---

## 🎉 Success Criteria

You've mastered this tutorial when you can:

✅ Explain how backpropagation works
✅ Implement Value class from memory
✅ Draw the transformer architecture
✅ Explain what attention does and why it's useful
✅ Implement a training loop from scratch
✅ Generate text with your model
✅ Debug gradient flow issues
✅ Modify the architecture (add layers, change dimensions)

---

**Ready to start? Run `python test_microgpt.py` now!** 🚀
