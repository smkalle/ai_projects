# MicroGPT Tutorial: Building a Transformer from Scratch

A comprehensive, beginner-friendly tutorial for understanding and implementing a GPT model in pure Python with zero dependencies.

Based on [Andrej Karpathy's minimal GPT implementation](https://gist.github.com/karpathy/8627fe009c40f57531cb18360106ce95).

## 📚 What You'll Learn

This tutorial teaches you the fundamentals of transformer architecture by building everything from scratch:

1. **Automatic Differentiation** - Build a custom autograd engine for backpropagation
2. **Tokenization** - Convert text to numbers and back
3. **Embeddings** - Token and position embeddings
4. **Self-Attention** - The core mechanism of transformers
5. **Multi-Head Attention** - Parallel attention patterns
6. **Transformer Architecture** - Attention blocks, MLP, residual connections
7. **RMSNorm** - Normalization for stable training
8. **Adam Optimizer** - Adaptive learning rate optimization
9. **Training Loop** - Forward pass, loss computation, backpropagation
10. **Text Generation** - Autoregressive sampling with temperature control

## 🚀 Quick Start

### Option 1: Run the Test Script (Fastest)
```bash
python test_microgpt.py
```

This verifies all components work correctly without training.

### Option 2: Train and Generate (5-10 minutes)
```bash
python microgpt_simple.py
```

This trains a small GPT model and generates 20 new names.

### Option 3: Interactive Tutorial (Recommended for Learning)
```bash
jupyter notebook microgpt_tutorial.ipynb
```

This opens the detailed, step-by-step tutorial with explanations, visualizations, and experiments.

## 📁 Files

- **`microgpt_tutorial.ipynb`** - Main tutorial notebook with detailed explanations
- **`microgpt_simple.py`** - Standalone training script
- **`test_microgpt.py`** - Quick test to verify everything works
- **`input.txt`** - Training data (auto-downloaded if not present)
- **`README.md`** - This file

## 📖 Tutorial Structure

### Part 0: Setup
- Imports and environment setup
- Pure Python - no external dependencies!

### Part 1: Autograd (Value Class)
- Understanding automatic differentiation
- Implementing forward and backward passes
- Testing gradient computation

**Key Concept**: The `Value` class wraps numbers and tracks computation graphs, enabling automatic gradient calculation.

### Part 2: Dataset & Tokenization
- Loading the names dataset (32K names)
- Character-level tokenization
- Understanding the BOS (Beginning of Sequence) token

**Key Concept**: Tokenization converts text into numbers that neural networks can process.

### Part 3: Model Components
- **Linear layers** - Matrix multiplication
- **Softmax** - Converting logits to probabilities
- **RMSNorm** - Normalization for stable training

**Key Concept**: These building blocks combine to create the transformer architecture.

### Part 4: Model Parameters
- Initializing weight matrices
- Understanding model dimensions
- Parameter counting

**Model Size**: ~8,000 parameters
- Embedding dimension: 16
- Attention heads: 4
- Layers: 1
- Context length: 16

### Part 5: GPT Architecture
- Token and position embeddings
- Multi-head self-attention mechanism
- MLP (feedforward) layers
- Residual connections

**Key Concept**: The transformer processes tokens sequentially, with each token attending to all previous tokens.

### Part 6: Adam Optimizer
- First and second moment estimation
- Bias correction
- Adaptive learning rates

**Key Concept**: Adam adapts the learning rate for each parameter, leading to faster and more stable training.

### Part 7: Training Loop
- Forward pass: predicting next characters
- Loss computation: cross-entropy
- Backward pass: gradient computation
- Parameter updates: Adam optimizer

**Training**: 1,000 steps on 32K names (~5-10 minutes)

### Part 8: Text Generation
- Autoregressive sampling
- Temperature control
- Comparing different temperatures

**Key Concept**: Temperature controls creativity - lower values are more conservative, higher values are more random.

### Part 9: Understanding & Analysis
- Recap of key concepts
- Architectural insights
- How transformers work

### Part 10: Experiments
- Analyzing training examples
- Testing on real names
- Visualizing attention patterns

## 🎯 Learning Outcomes

After completing this tutorial, you will:

✅ Understand how automatic differentiation enables neural network training
✅ Know how transformers process sequential data
✅ Understand self-attention and why it's powerful
✅ Be able to implement a GPT model from scratch
✅ Understand the training process: forward pass, loss, backward pass, optimization
✅ Know how to generate text with language models

## 💡 Key Insights

### Why This Tutorial?

1. **Zero Dependencies** - Pure Python implementation helps you understand fundamentals without framework magic
2. **Complete Algorithm** - Every line is essential; nothing hidden in libraries
3. **Educational Focus** - Prioritizes clarity and understanding over efficiency
4. **Step-by-Step** - Detailed logging and explanations at every stage

### What Makes Transformers Special?

- **Self-Attention** - Tokens can look at all previous tokens, capturing long-range dependencies
- **Parallelization** - Unlike RNNs, transformers can process sequences in parallel during training
- **Scalability** - Architecture scales effectively from millions to billions of parameters
- **Versatility** - Same architecture works for many tasks: text, code, images, etc.

## 🧪 Experiments to Try

Once you complete the tutorial, experiment with:

1. **Hyperparameters**
   - Increase `n_embd` (16 → 32 or 64)
   - Add more layers (`n_layer = 2` or `3`)
   - Adjust learning rate
   - Train for more steps

2. **Architecture**
   - Implement LayerNorm instead of RMSNorm
   - Try different activation functions (GeLU instead of ReLU)
   - Add dropout for regularization

3. **Data**
   - Train on different datasets (words, code snippets)
   - Try different tokenization schemes (word-level, BPE)
   - Mix multiple languages

4. **Analysis**
   - Plot loss curves
   - Visualize attention patterns
   - Analyze learned embeddings
   - Test on unseen names

## 📊 Expected Results

After training for 1,000 steps:

- **Loss**: Should decrease from ~3.5 to ~2.0
- **Generated Names**: Should look plausible (e.g., "aria", "leon", "maya")
- **Training Time**: 5-10 minutes on modern CPU

### Sample Output

```
Generated names (temperature=0.5):
  1. aria
  2. leon
  3. maya
  4. kira
  5. finn
  ...
```

## 🔍 Troubleshooting

### "ModuleNotFoundError"
- Solution: This tutorial uses only standard library - no installation needed!

### "input.txt not found"
- Solution: The script auto-downloads it. Ensure internet connection.

### Training is slow
- Normal: Pure Python is ~100x slower than optimized frameworks
- Expected: 1-2 steps per second on CPU
- Patience: 1,000 steps takes 5-10 minutes

### Generated names look random
- Possible causes:
  - Not enough training steps (try 2,000-5,000)
  - Learning rate too high/low
  - Model too small (try increasing `n_embd`)

### Memory errors
- Reduce `block_size` (16 → 8)
- Reduce `n_embd` (16 → 8)
- Process smaller batches

## 📚 Further Reading

### Papers
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - Original transformer paper
- [Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) - GPT-1 paper
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) - GPT-2 paper

### Videos
- [Andrej Karpathy - Neural Networks: Zero to Hero](https://www.youtube.com/watch?v=VMj-3S1tku0&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ)
- [3Blue1Brown - But what is a GPT?](https://www.youtube.com/watch?v=wjZofJX0v4M)

### Resources
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html)

## 🙏 Credits

- **Original Implementation**: [Andrej Karpathy](https://github.com/karpathy)
- **Dataset**: Names from [makemore](https://github.com/karpathy/makemore)
- **Inspiration**: Educational approach to understanding transformers

## 📝 License

This tutorial is educational material based on Karpathy's public gist. Use freely for learning!

## 🤝 Contributing

Found an issue or have suggestions? This is a tutorial project - feel free to:
- Report bugs
- Suggest improvements
- Share your experiments
- Add more detailed explanations

---

## 🎓 Next Steps After This Tutorial

Once you master this implementation:

1. **Study PyTorch Implementation** - See how frameworks optimize these operations
2. **Build Larger Models** - Scale up parameters and layers
3. **Try Different Tasks** - Apply to different domains (code, music, etc.)
4. **Explore Optimizations** - Implement Flash Attention, KV caching, etc.
5. **Fine-tuning** - Learn to adapt pre-trained models
6. **Modern Architectures** - Study BERT, GPT-3, LLaMA, etc.

---

**Happy Learning! 🚀**

Start with `python test_microgpt.py` to verify everything works, then dive into the tutorial notebook!
