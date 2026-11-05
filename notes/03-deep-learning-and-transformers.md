# Deep Learning & Transformers – Complete Developer Study Notes 🧠⚡

> Every LLM is a Transformer. Understand neurons, backpropagation and attention, and "how does ChatGPT/Claude work?" becomes an easy question.

[⬅ Previous: Machine Learning](02-machine-learning.md) | [🏠 Home](../README.md) | [Next: Training Data ➡](04-training-data.md)

## 📚 What's covered

✅ [Neural network building blocks](#1-neural-network-building-blocks)
✅ [Activation functions](#2-activation-functions)
✅ [How training works: loss, gradient descent, backpropagation](#3-how-training-works)
✅ [Optimizers & regularisation](#4-optimizers--regularisation)
✅ [CNNs, RNNs/LSTMs](#5-architectures-cnn-rnn-lstm)
✅ [The Transformer and self-attention](#6-the-transformer)
✅ [Encoder vs decoder models (BERT vs GPT)](#7-encoder-decoder-and-encoder-decoder)
✅ [Tokens, context windows, temperature](#8-tokens-context-windows-sampling)
✅ [Transfer learning & fine-tuning (LoRA, QLoRA, RLHF)](#9-transfer-learning--fine-tuning)
✅ [PyTorch mini example](#10-pytorch-mini-example)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** ML engineers, GenAI developers, and anyone who must explain how LLMs work.

---

## 1. Neural network building blocks

```
inputs x1..xn ──► weighted sum (w·x + b) ──► activation f() ──► output
                    one neuron

Input layer ──► Hidden layer(s) ──► Output layer      ("deep" = many hidden layers)
```

| Term | Meaning |
|---|---|
| **Weight** | How strongly an input influences a neuron (learned) |
| **Bias** | Offset that shifts the activation (learned) |
| **Layer** | A group of neurons computed together (a matrix multiplication) |
| **Epoch** | One full pass over the training data |
| **Batch** | A subset of examples processed before one weight update |
| **Learning rate** | Size of each weight update step |

## 2. Activation functions

| Function | Output | Used for |
|---|---|---|
| **ReLU** max(0, x) | 0 → ∞ | Default for hidden layers (fast, avoids vanishing gradients) |
| **GELU / SwiGLU** | Smooth ReLU variants | Transformers / LLMs |
| **Sigmoid** | 0 → 1 | Binary classification output |
| **Softmax** | Probabilities that sum to 1 | Multi-class output; LLM next-token probabilities |
| **Tanh** | -1 → 1 | Older RNNs |

Without non-linear activations, stacking layers would still only compute a linear function.

## 3. How training works

```
1. Forward pass   : input → prediction
2. Loss           : how wrong?  (MSE for regression, cross-entropy for classification/LLMs)
3. Backward pass  : backpropagation computes the gradient of the loss for every weight (chain rule)
4. Update         : w = w - learning_rate × gradient     (gradient descent)
5. Repeat for many batches and epochs
```

- **Vanishing gradients:** gradients shrink to ~0 in deep networks, so early layers stop learning. Fixed by ReLU, residual (skip) connections, normalisation.
- **Exploding gradients:** gradients blow up. Fixed by gradient clipping and normalisation.

## 4. Optimizers & regularisation

| Optimizer | Note |
|---|---|
| SGD (+ momentum) | Simple, strong with tuning |
| **Adam / AdamW** | Adaptive learning rates; AdamW is the default for Transformers |

| Regularisation | What it does |
|---|---|
| **Dropout** | Randomly switches off neurons during training |
| **Weight decay (L2)** | Penalises large weights |
| **Early stopping** | Stop when validation loss stops improving |
| **Batch / layer normalisation** | Stabilises and speeds up training (LayerNorm in Transformers) |
| **Data augmentation** | More varied training data (image flips, crops) |

## 5. Architectures: CNN, RNN, LSTM

| Architecture | Built for | Key idea | Today |
|---|---|---|---|
| **CNN** | Images, video | Convolution filters detect edges → shapes → objects | Still common in vision (with Vision Transformers) |
| **RNN** | Sequences | Reads one step at a time, keeps a hidden state | Mostly replaced by Transformers |
| **LSTM / GRU** | Long sequences | Gates control what to remember/forget | Some time-series uses |
| **Transformer** | Text, images, audio, code | Self-attention over the whole sequence in parallel | **Foundation of LLMs** |

## 6. The Transformer

**Self-attention:** every token looks at every other token and decides how much each one matters to its meaning.

```
"The animal didn't cross the street because IT was too tired."
                                              │
              attention: "it" ──strongly──► "animal"   (not "street")
```

How it works:
1. Each token becomes an **embedding** vector, plus **positional information** (order matters).
2. For each token the model computes three vectors: **Query (Q)**, **Key (K)**, **Value (V)**.
3. Attention scores = similarity of a token's Query with every Key: `softmax(Q·Kᵀ / √d) · V`.
4. **Multi-head attention** runs several attention "heads" in parallel; each learns different relationships (grammar, references, topic).
5. A **feed-forward network**, **residual connections** and **layer normalisation** follow; the block repeats N times (dozens of layers in an LLM).

**Why Transformers won:** they process tokens in parallel (fast on GPUs), handle long-range context, and scale predictably with more data and compute.

## 7. Encoder, decoder, and encoder-decoder

| Type | Sees | Good at | Examples |
|---|---|---|---|
| **Encoder-only** | Whole input (bidirectional) | Understanding: classification, embeddings, search | BERT, many embedding models |
| **Decoder-only** | Previous tokens only (causal) | **Generating text** | GPT, Claude, Llama, Mistral |
| **Encoder-decoder** | Encoder reads input, decoder writes output | Translation, summarisation | T5, BART |

**How an LLM generates:** predict the next token's probability distribution → pick one → append it → repeat (autoregressive generation).

## 8. Tokens, context windows, sampling

| Term | Meaning |
|---|---|
| **Token** | A piece of text (≈ ¾ of an English word). Models read, write and **bill** in tokens |
| **Context window** | Max tokens (prompt + output) the model can consider at once |
| **Temperature** | Randomness. 0 → focused/deterministic, higher → more creative |
| **Top-p (nucleus)** | Sample only from the most likely tokens whose probabilities add up to p |
| **Max tokens** | Limit on output length |
| **Stop sequences** | Strings that end generation |

## 9. Transfer learning & fine-tuning

| Technique | What it is | When |
|---|---|---|
| **Transfer learning** | Start from a pre-trained model and adapt it | Almost always better than training from scratch |
| **Full fine-tuning** | Update all weights on your data | Big budget, big data |
| **PEFT / LoRA** | Train small low-rank adapter matrices; freeze the base model | Most fine-tuning today; cheap and fast |
| **QLoRA** | LoRA on a 4-bit quantised base model | Fine-tune large models on one GPU |
| **SFT** (supervised fine-tuning) | Train on prompt → ideal-response pairs | Teach format, tone, task |
| **RLHF** | Humans rank outputs; a reward model trains the LLM with RL | Align with human preferences |
| **DPO** | Learns directly from preferred-vs-rejected pairs, without a reward model | Simpler alternative to RLHF |
| **Distillation** | A small "student" learns from a large "teacher" | Cheaper, faster models |
| **Quantisation** | Store weights in fewer bits (8/4-bit) | Smaller, faster inference |

**Prompting vs RAG vs fine-tuning (very common question):**

| Need | Best first choice |
|---|---|
| Change format, tone, or simple behaviour | **Prompt engineering** |
| Answer from **your own / changing** documents | **RAG** |
| Teach a consistent style or a narrow specialised task, or cut cost with a smaller model | **Fine-tuning** |

## 10. PyTorch mini example

```python
# pip install torch
import torch
from torch import nn

X = torch.randn(256, 4)                       # 256 samples, 4 features
y = (X.sum(dim=1) > 0).long()                 # simple synthetic label

model = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 2))
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.AdamW(model.parameters(), lr=0.01)

for epoch in range(50):
    logits = model(X)                         # 1. forward
    loss = loss_fn(logits, y)                 # 2. loss
    opt.zero_grad(); loss.backward()          # 3. backprop
    opt.step()                                # 4. update

acc = (model(X).argmax(dim=1) == y).float().mean()
print(f"loss={loss.item():.3f} accuracy={acc:.2%}")
```

---

## 💬 Interview questions & answers

**Q1. Explain self-attention in two sentences.**
Each token creates a query, key and value; it compares its query with every other token's key to get attention weights, then takes a weighted sum of their values. This lets every word use context from the whole sequence.

**Q2. Why divide by √d in attention?**
Dot products grow with vector size, which pushes softmax into regions with tiny gradients. Scaling keeps training stable.

**Q3. BERT vs GPT?**
BERT is an encoder that reads text in both directions. It's good for understanding and embeddings. GPT is a decoder that only sees previous tokens and is built to generate text.

**Q4. What is LoRA and why is it popular?**
It freezes the base model and trains small low-rank adapter matrices added to some layers. That's a tiny fraction of the parameters, so it needs much less GPU memory and storage, and you can swap adapters per task.

**Q5. When would you fine-tune instead of using RAG?**
When you need consistent style or format, a narrow skill the base model lacks, or a smaller, cheaper model for a high-volume task. Use RAG when knowledge changes or answers must cite sources. They're often combined.

**Q6. What causes vanishing gradients and how are they fixed?**
Repeated multiplication of small derivatives through many layers. Fixes are ReLU-family activations, residual connections, normalisation, and careful initialisation.

**Q7. What does temperature do?**
It scales the logits before softmax. Low temperature makes the most likely token dominate (deterministic). High temperature flattens the distribution (more varied and creative, but more errors).

**Q8. What is a context window and why does it matter?**
The maximum number of tokens the model can consider. It limits how much conversation, documents or retrieved chunks you can include, and affects cost and latency.

---

## ✅ Final revision checklist

- [ ] I can explain forward pass, loss, backprop and gradient descent.
- [ ] I know when to use ReLU, sigmoid and softmax.
- [ ] I can describe Q, K, V and multi-head attention.
- [ ] I can compare encoder-only, decoder-only and encoder-decoder models.
- [ ] I can explain tokens, context window, temperature and top-p.
- [ ] I can compare prompting vs RAG vs fine-tuning, and LoRA vs full fine-tuning.

## 🔗 Official docs
- PyTorch tutorials: https://pytorch.org/tutorials/
- Hugging Face course: https://huggingface.co/learn
- "Attention Is All You Need": https://arxiv.org/abs/1706.03762

---
*My AI Engineering Study Notes* | [⬅ Previous](02-machine-learning.md) | [🏠 Home](../README.md) | [Next ➡](04-training-data.md)
