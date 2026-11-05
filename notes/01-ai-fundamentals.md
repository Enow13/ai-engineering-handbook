# Artificial Intelligence – Complete Developer Study Notes 🤖🧠

> AI is not one technology. It is a stack: data → models → applications → operations. Know every layer and you can talk to anyone in the room.

[🏠 Home](../README.md) | [Next: Machine Learning ➡](02-machine-learning.md)

## 📚 What's covered

✅ [What AI is (and isn't)](#1-what-ai-is-and-isnt)
✅ [Types of AI: narrow, general, generative, agentic](#2-types-of-ai)
✅ [The AI family tree: AI ⊃ ML ⊃ DL ⊃ GenAI](#3-the-ai-family-tree)
✅ [A short history that interviewers like](#4-a-short-history)
✅ [How an AI system works end to end](#5-how-an-ai-system-works-end-to-end)
✅ [The math you actually need](#6-the-math-you-actually-need)
✅ [Real-world applications by industry](#7-real-world-applications)
✅ [Responsible AI](#8-responsible-ai)
✅ [The modern AI engineer's skill map](#9-the-ai-engineers-skill-map)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** beginners, career switchers, and anyone who needs to explain AI clearly in an interview.

---

## 1. What AI is (and isn't)

**Artificial Intelligence** = computer systems that perform tasks that normally need human intelligence: understanding language, recognising images, making predictions, planning, deciding.

| AI **is** | AI **is not** |
|---|---|
| Pattern recognition learned from data | Magic, or "thinking" like a human |
| Probabilistic: gives the *most likely* answer | Guaranteed correct |
| Only as good as its data and design | Neutral by default: it inherits bias from data |
| A tool inside a larger system | A complete product on its own |

💡 **One-line definition for interviews:** *"AI is software that learns patterns from data to make predictions, generate content or take actions, instead of following only hand-written rules."*

### Rules vs learning

```
Traditional programming:   Rules + Data  ──►  Answers
Machine learning:          Data + Answers ──►  Rules (a model)
```

## 2. Types of AI

| Type | What it does | Example |
|---|---|---|
| **Narrow AI** (all AI today) | One task or a family of tasks | Spam filter, fraud detection, ChatGPT/Claude |
| **General AI (AGI)** | Any intellectual task a human can do | Research goal, not a product |
| **Predictive AI** | Predicts a value or class | Will this customer churn? Price of this house? |
| **Generative AI** | Creates new content: text, images, code, audio | Claude, GPT, DALL·E, Copilot |
| **Agentic AI** | Plans and takes actions with tools to reach a goal | An agent that reads a ticket, queries a DB and resets a password |

## 3. The AI family tree

```
┌──────────────────────────────── Artificial Intelligence ─────────────────────────────┐
│  rules, search, planning, expert systems ...                                          │
│   ┌──────────────────────────── Machine Learning ───────────────────────────────┐    │
│   │  learns from data: regression, trees, clustering ...                          │    │
│   │   ┌──────────────────────── Deep Learning ──────────────────────────────┐    │    │
│   │   │  neural networks with many layers: CNN, RNN, Transformers            │    │    │
│   │   │   ┌──────────────── Generative AI / LLMs ──────────────────┐        │    │    │
│   │   │   │  creates content: GPT, Claude, Llama, Gemini            │        │    │    │
│   │   │   └─────────────────────────────────────────────────────────┘        │    │    │
│   │   └──────────────────────────────────────────────────────────────────────┘    │    │
│   └───────────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

## 4. A short history

| Year | Milestone | Why it matters |
|---|---|---|
| 1950 | Turing Test | "Can machines think?" |
| 1956 | Dartmouth workshop, the term "AI" | Birth of the field |
| 1980s | Expert systems | Rules written by humans; brittle |
| 1997 | Deep Blue beats Kasparov | Search + compute |
| 2012 | AlexNet (deep CNN) wins ImageNet | Deep learning era begins (GPUs + big data) |
| 2017 | "Attention Is All You Need" (Transformer) | Foundation of every modern LLM |
| 2018–2020 | BERT, GPT-2, GPT-3 | Pre-trained language models |
| 2022 | ChatGPT | GenAI goes mainstream |
| 2023–2024 | RAG, open models (Llama), multimodal models | Enterprise adoption |
| 2025–2026 | Agents, MCP, A2A, agent platforms (Foundry, Bedrock AgentCore) | AI that **acts**, not just answers |

## 5. How an AI system works end to end

```
 Business problem
      │
      ▼
 Data (collect, label, clean)  ──►  Model (train or choose a foundation model)
      │                                   │
      ▼                                   ▼
 Evaluation (accuracy, safety, cost)  ──►  Deployment (API, app, agent)
                                          │
                                          ▼
                                Monitoring (drift, quality, cost) ──► retrain / improve
```

The model is often the **smallest** part. Data, evaluation, deployment and monitoring are where most of the engineering effort goes. That's why MLOps exists ([notes 15–17](15-mlops-fundamentals.md)).

## 6. The math you actually need

| Area | What to know | Where it shows up |
|---|---|---|
| **Linear algebra** | Vectors, matrices, dot product, matrix multiplication | Embeddings, neural network layers, attention |
| **Probability** | Probability distributions, conditional probability, Bayes' rule | Classification, LLM next-token prediction |
| **Statistics** | Mean, variance, standard deviation, correlation, sampling, hypothesis tests | Data analysis, A/B tests, evaluation |
| **Calculus** | Derivatives, gradients, chain rule | Training (gradient descent, backpropagation) |

**Cosine similarity** (asked constantly in RAG interviews):

```
cos(A, B) = (A · B) / (‖A‖ × ‖B‖)      →  1 = same direction, 0 = unrelated, -1 = opposite
```

## 7. Real-world applications

| Industry | Use case | Type |
|---|---|---|
| Healthcare | Diagnose from images, predict readmission, summarise clinical notes | Predictive + GenAI |
| Finance | Fraud detection, credit scoring, document extraction | Predictive |
| Retail | Recommendations, demand forecasting, shopping assistants | Predictive + Agentic |
| Manufacturing | Predictive maintenance, visual defect detection | Predictive + CV |
| Enterprise IT | Knowledge assistants (RAG), ticket triage agents, code assistants | GenAI + Agentic |
| Customer service | Chatbots with human escalation, call summarisation | GenAI |

## 8. Responsible AI

Microsoft, AWS and Google all publish similar principles. Remember them as **FRTPIA**:

| Principle | Practical meaning |
|---|---|
| **F**airness | Test outcomes across groups (gender, age, region) |
| **R**eliability & safety | Evaluate, add guardrails, plan for failure |
| **T**ransparency | Explain how it works and its limits; cite sources in RAG |
| **P**rivacy & security | Protect PII, least-privilege access, no secrets in prompts |
| **I**nclusiveness | Works for people with different abilities and languages |
| **A**ccountability | A human owns the system and its decisions |

Regulation to name-drop: **EU AI Act** (risk-based rules), **NIST AI Risk Management Framework** (US), **ISO/IEC 42001** (AI management systems).

## 9. The AI engineer's skill map

```
Foundations     Python · SQL · Git · Linux · statistics
Classic ML      scikit-learn · pandas · feature engineering · evaluation
Deep learning   PyTorch · Transformers · Hugging Face
GenAI           Prompting · RAG · embeddings · vector DBs · evaluation
Agents          Tool calling · LangChain/LangGraph · MCP · A2A · memory · guardrails
Cloud           Azure (Foundry, Azure ML, AI Search) · AWS (Bedrock, SageMaker AI)
MLOps/LLMOps    Docker · Kubernetes · CI/CD · MLflow · monitoring · cost control
Soft skills     Explaining trade-offs · business value · documentation
```

---

## 💬 Interview questions & answers

**Q1. What's the difference between AI, ML and deep learning?**
AI is the broad goal of machines doing intelligent tasks. ML is a subset where systems learn from data instead of fixed rules. Deep learning is a subset of ML that uses multi-layer neural networks, which is what powers modern vision and language models.

**Q2. What's the difference between predictive and generative AI?**
Predictive AI outputs a label or number (fraud / not fraud, a price). Generative AI produces new content (text, images, code) by learning the distribution of its training data.

**Q3. What makes an AI system "agentic"?**
It can pursue a goal over several steps: plan, call tools (APIs, databases, code), observe results, and decide the next action, with some autonomy. A chatbot answers; an agent acts.

**Q4. Why is data more important than the algorithm?**
Garbage in, garbage out. A simple model on clean, representative, well-labelled data usually beats a complex model on poor data. Most production failures come from data issues: drift, bias, leakage, missing values.

**Q5. How would you explain a Transformer to a non-technical manager?**
It reads a whole sentence at once and learns which words matter to each other ("attention"), so it understands context much better than older models that read word by word.

**Q6. What is hallucination and how do you reduce it?**
The model confidently generates something false. You reduce it with grounding (RAG), instructions to say "I don't know", citations, lower temperature, evaluation, and human review for high-risk outputs.

**Q7. Name three Responsible AI risks and one mitigation each.**
Bias → fairness testing across groups. Privacy leakage → PII redaction and access control. Harmful output → content filters/guardrails plus red-teaming.

**Q8. What does an AI engineer do that a data scientist doesn't?**
Data scientists focus on analysis and building models. AI engineers focus on putting AI into production: APIs, RAG pipelines, agents, cloud infrastructure, evaluation, monitoring and cost.

---

## ✅ Final revision checklist

- [ ] I can define AI, ML, DL and GenAI in one sentence each.
- [ ] I can draw the AI family tree.
- [ ] I can explain the end-to-end AI lifecycle and why the model is the smallest part.
- [ ] I know the four maths areas and where each is used.
- [ ] I can compute and explain cosine similarity.
- [ ] I can list the six Responsible AI principles.
- [ ] I can give two real use cases for my target industry.

## 🔗 Official docs
- Microsoft Responsible AI: https://www.microsoft.com/ai/responsible-ai
- AWS Responsible AI: https://aws.amazon.com/ai/responsible-ai/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework

---
*My AI Engineering Study Notes* | [🏠 Home](../README.md) | [Next: Machine Learning ➡](02-machine-learning.md)
