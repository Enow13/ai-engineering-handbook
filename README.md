# 📚 My AI Engineering Study Notes

**Complete developer study notes for AI Engineers, GenAI Developers, ML/MLOps Engineers and interview candidates**: from AI fundamentals to RAG, Agentic AI, MCP, A2A, LangChain, LangGraph, Azure, AWS and MLOps on both clouds.

Each topic follows the same format: **what's covered → clear explanations, tables and diagrams → code → interview Q&A → final revision checklist → official docs**.

---

## 🗂️ Topics

| # | Topic | What you'll learn |
|---|---|---|
| 01 | [Artificial Intelligence Fundamentals](notes/01-ai-fundamentals.md) 🤖 | AI vs ML vs DL vs GenAI, history, maths, Responsible AI, skill map |
| 02 | [Machine Learning](notes/02-machine-learning.md) 📈 | Algorithms, splits, overfitting, metrics, feature engineering, tuning |
| 03 | [Deep Learning & Transformers](notes/03-deep-learning-and-transformers.md) 🧠 | Neural nets, backprop, CNN/RNN, attention, LLMs, LoRA, RLHF |
| 04 | [Training Data](notes/04-training-data.md) 🗂️ | Data quality, labelling, leakage, LLM datasets, JSONL, drift, cloud tools |
| 05 | [Generative AI & Prompt Engineering](notes/05-generative-ai-and-prompt-engineering.md) ✍️ | Model choice, prompting techniques, tool calling, injection, evaluation, cost |
| 06 | [RAG (Retrieval-Augmented Generation)](notes/06-rag.md) 🔎 | Architecture, chunking, hybrid search, reranking, advanced RAG, evaluation |
| 07 | [Embeddings & Vector Databases](notes/07-vector-databases-and-embeddings.md) 🧭 | Embeddings, HNSW/IVF, FAISS, Chroma, Pinecone, Qdrant, Azure AI Search, OpenSearch |
| 08 | [Agentic AI](notes/08-agentic-ai.md) 🛠️ | Agent loop, ReAct, patterns, multi-agent, memory, guardrails, evaluation |
| 09 | [MCP (Model Context Protocol)](notes/09-mcp.md) 🔌 | Host/client/server, tools/resources/prompts, transports, 2026 spec, security, **working Python server & client** |
| 10 | [A2A (Agent2Agent Protocol)](notes/10-a2a.md) 🤝 | Agent Cards, tasks, states, streaming, push notifications, A2A + MCP |
| 11 | [LangChain](notes/11-langchain.md) 🦜 | Models, LCEL, tools, `create_agent`, middleware, structured output, RAG blocks |
| 12 | [LangGraph](notes/12-langgraph.md) 🕸️ | State graphs, routing, checkpointers, human-in-the-loop, memory, multi-agent |
| 13 | [Azure AI & Data Services](notes/13-azure-ai-services.md) 🔷 | Microsoft Foundry, Azure OpenAI, Agent Service, AI Search, Foundry Tools, Azure ML |
| 14 | [AWS AI & Data Services](notes/14-aws-ai-services.md) 🟧 | Bedrock, Knowledge Bases, Guardrails, AgentCore, SageMaker AI, Azure↔AWS mapping |
| 15 | [MLOps & LLMOps Fundamentals](notes/15-mlops-fundamentals.md) 🔁 | Lifecycle, maturity, MLflow, CI/CD/CT, deployment patterns, monitoring, LLMOps |
| 16 | [MLOps on Azure](notes/16-mlops-on-azure.md) 🔷 | Azure ML jobs, sweeps, pipelines, registries, endpoints, monitoring, GitHub Actions |
| 17 | [MLOps on AWS](notes/17-mlops-on-aws.md) 🟧 | SageMaker AI SDK v3, Pipelines, Model Registry, endpoints, Model Monitor, CI/CD |
| 18 | [Git](notes/18-git.md) 🌿 | Commands, branching, conflicts, undoing, rebasing, strategies, common errors |

---

## 💻 Runnable code (no API keys needed)

All examples were run successfully before publishing. See [`code/README.md`](code/README.md).

| File | Shows | Topic |
|---|---|---|
| [`code/rag_minimal.py`](code/rag_minimal.py) | Retrieval with scores, relevance threshold, grounded prompt | RAG |
| [`code/mcp_server.py`](code/mcp_server.py) + [`code/mcp_client.py`](code/mcp_client.py) | A real MCP server (tools, resource, prompt) and a client that uses it | MCP |
| [`code/langchain_agent.py`](code/langchain_agent.py) | A tool-calling agent with `create_agent` (offline stand-in model) | LangChain |
| [`code/langgraph_workflow.py`](code/langgraph_workflow.py) | Routing, checkpointing and human-in-the-loop approval | LangGraph |

---

## 🚀 How to use these notes

### Read on GitHub (easiest)
Click any topic in the table. GitHub formats the notes, and every page has **Previous / Home / Next** links.

### Clone and run the code
```bash
git clone https://github.com/Enow13/ai-engineering-handbook.git
cd ai-engineering-handbook
python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cd code
python rag_minimal.py
python mcp_client.py
python langchain_agent.py
python langgraph_workflow.py
```
Requires **Python 3.10+**. To pull new notes later: `git pull`.

### Suggested study paths

| Goal | Order |
|---|---|
| **New to AI** | 01 → 02 → 03 → 04 → 05 → 18 |
| **GenAI / RAG Engineer** | 05 → 06 → 07 → 11 → 13 or 14 |
| **Agentic AI Developer** | 05 → 08 → 09 → 10 → 11 → 12 |
| **MLOps Engineer** | 02 → 04 → 15 → 16 → 17 → 18 |
| **Azure AI Engineer** | 05 → 06 → 13 → 16 |
| **AWS AI Engineer** | 05 → 06 → 14 → 17 |
| **Interview next week** | Read each note's **Interview Q&A** and **Final revision checklist** |


---

## ⚠️ Keeping up to date

AI moves fast. These notes reflect the state of things in **October 2026**, including:
- **MCP spec 2026-07-28** (stateless requests, no `initialize` handshake) and **MCP Python SDK v2** (`FastMCP` → `MCPServer`)
- **A2A v1.0** (Agent Card at `/.well-known/agent-card.json`)
- **LangChain / LangGraph 1.x** (`create_agent`, middleware)
- **SageMaker Python SDK v3** (`ModelTrainer`, `ModelBuilder`; `Estimator` removed)
- **Microsoft Foundry** (formerly Azure AI Foundry) naming

Model names, prices and service features change often. Always confirm details in the **official docs** linked at the end of each note.

---

🔖 **Save, star ⭐ and share** this repo with someone preparing for an AI role.
💬 Questions or corrections? Open an **Issue** on this repo.

*My AI Engineering Study Notes*
