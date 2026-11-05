# LangChain – Complete Developer Study Notes 🦜🔗

> LangChain is the fastest way to build an LLM app or agent that works with any model provider. Since v1.0 it's built on LangGraph, so you can start simple and drop down for more control.

[⬅ Previous: A2A](10-a2a.md) | [🏠 Home](../README.md) | [Next: LangGraph ➡](12-langgraph.md)

## 📚 What's covered

✅ [What LangChain is & the package layout](#1-what-langchain-is)
✅ [Chat models & `init_chat_model` (any provider)](#2-chat-models)
✅ [Messages & prompt templates](#3-messages--prompt-templates)
✅ [LCEL: composing chains with `|`](#4-lcel-chains)
✅ [Tools](#5-tools)
✅ [Agents with `create_agent`](#6-agents-with-create_agent)
✅ [Middleware: human-in-the-loop, PII, summarisation, limits, fallbacks](#7-middleware)
✅ [Structured output](#8-structured-output)
✅ [RAG building blocks: loaders, splitters, embeddings, vector stores, retrievers](#9-rag-building-blocks)
✅ [Memory](#10-memory)
✅ [Using Azure OpenAI and Amazon Bedrock](#11-azure-and-aws)
✅ [LangSmith: tracing & evaluation](#12-langsmith)
✅ [LangChain vs LlamaIndex vs Haystack](#13-langchain-vs-llamaindex-vs-haystack)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** Python developers building LLM apps, RAG systems and agents.

---

## 1. What LangChain is

An open-source framework (Python and JavaScript) providing **standard interfaces** for models, tools, retrievers and agents, plus **hundreds of integrations**, so you can swap providers without rewriting code.

| Package | Contains |
|---|---|
| `langchain` | `create_agent`, middleware, `init_chat_model`, high-level APIs |
| `langchain-core` | Base interfaces: messages, prompts, runnables, tools, output parsers |
| `langchain-<provider>` | Integrations: `langchain-anthropic`, `langchain-openai`, `langchain-aws`, `langchain-google-genai`, `langchain-ollama`... |
| `langchain-community` | Community integrations |
| `langchain-text-splitters` | Chunking utilities |
| `langchain-classic` | Legacy v0.x features (old chains, `AgentExecutor`) |
| `langgraph` | The runtime agents run on ([note 12](12-langgraph.md)) |
| **LangSmith** | Hosted tracing, evaluation and prompt management |

**v1.0 (Oct 2025) key points:** `create_agent` replaces `langgraph.prebuilt.create_react_agent`; **middleware** for customisation; standard **content blocks** across providers; legacy moved to `langchain-classic`; Python 3.10+.

```bash
pip install langchain langchain-anthropic          # or langchain-openai / langchain-aws
```

## 2. Chat models

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-5-5", temperature=0)   # "provider:model"
# model = init_chat_model("openai:gpt-5-mini")
# model = init_chat_model("bedrock_converse:anthropic.claude-...")      # AWS (langchain-aws)

reply = model.invoke("Explain RAG in one sentence.")
print(reply.content)

for chunk in model.stream("Write a haiku about Kubernetes"):          # streaming
    print(chunk.content, end="")

replies = model.batch(["Define MLOps", "Define LLMOps"])               # parallel batch
```

Every model shares the same **Runnable** interface: `invoke`, `stream`, `batch`, plus async `ainvoke`, `astream` and `abatch`.

## 3. Messages & prompt templates

| Message | Role |
|---|---|
| `SystemMessage` | Instructions |
| `HumanMessage` | User input |
| `AIMessage` | Model output (may contain `tool_calls`) |
| `ToolMessage` | A tool's result, linked by `tool_call_id` |

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Answer in under {words} words."),
    ("human", "{question}"),
])
messages = prompt.invoke({"role": "cloud architect", "words": 50, "question": "What is a VNet?"})
```

## 4. LCEL chains

**LCEL (LangChain Expression Language)** composes runnables with the pipe `|`: the output of one becomes the input of the next.

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()
print(chain.invoke({"role": "security engineer", "words": 40, "question": "What is MFA?"}))
```

Useful runnables: `RunnablePassthrough` (pass input through), `RunnableParallel` (run branches in parallel), `RunnableLambda` (wrap any function), `.with_retry()`, `.with_fallbacks([...])`.

💡 Use **chains** for fixed pipelines (summarise, extract, classify). Use **agents** when the model must decide which tools to call.

## 5. Tools

```python
from langchain_core.tools import tool

@tool
def get_ticket_status(ticket_id: int) -> str:
    """Return the status of an IT ticket by its numeric id."""   # the model reads this docstring
    return f"Ticket {ticket_id} is in progress"
```

The function name, docstring and type hints become the tool's schema. Write descriptions for the **LLM**: say when to use the tool and what it returns. You can also load tools from **MCP servers** with the `langchain-mcp-adapters` package.

## 6. Agents with create_agent

`create_agent` builds a production-ready tool-calling agent (the ReAct loop) running on LangGraph.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-5-5",
    tools=[get_ticket_status],
    system_prompt="You are Contoso's IT helpdesk agent. Use tools for facts.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "What's the status of ticket 1042?"}]})
print(result["messages"][-1].content)
```

**Runnable example with no API key:** [`code/langchain_agent.py`](../code/langchain_agent.py) uses a scripted stand-in model so you can watch the loop (Human → AI tool call → Tool result → AI answer). Set `MODEL=anthropic:claude-sonnet-5-5` (plus the provider package and API key) to use a real model.

```bash
cd code && python langchain_agent.py
```

## 7. Middleware

Middleware hooks into the agent loop (before/after the model, around tool calls) for control without rewriting the agent.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware, PIIMiddleware, SummarizationMiddleware,
    ModelCallLimitMiddleware, ModelFallbackMiddleware,
)
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="anthropic:claude-sonnet-5-5",
    tools=[get_ticket_status, create_ticket],
    middleware=[
        PIIMiddleware("email", strategy="redact"),                         # redact emails in input
        SummarizationMiddleware(model="anthropic:claude-haiku-5-5",
                                trigger=("tokens", 4000)),                 # summarise long chats
        HumanInTheLoopMiddleware(interrupt_on={"create_ticket": True}),    # approve before running
        ModelCallLimitMiddleware(run_limit=10),                            # stop runaway loops
        ModelFallbackMiddleware("openai:gpt-5-mini"),                      # fallback if the model fails
    ],
    checkpointer=InMemorySaver(),          # required for human-in-the-loop (pause/resume)
)
```

Other built-ins include tool retry, tool-call limits, context editing, to-do lists and LLM tool selection. You can write your own by subclassing `AgentMiddleware`.

## 8. Structured output

```python
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    category: str = Field(description="hardware, software, access or network")
    priority: str = Field(description="low, medium or high")
    summary: str

# On a model:
triage = model.with_structured_output(Ticket)
t = triage.invoke("My laptop won't turn on and I have a client demo in an hour")
print(t.priority)          # a validated Pydantic object

# On an agent:
agent = create_agent(model="anthropic:claude-sonnet-5-5", tools=[], response_format=Ticket)
# result["structured_response"] holds the Ticket
```

## 9. RAG building blocks

| Block | Purpose | Examples |
|---|---|---|
| **Document loaders** | Read sources into `Document` objects (text + metadata) | `PyPDFLoader`, `WebBaseLoader`, `CSVLoader`, SharePoint and S3 loaders |
| **Text splitters** | Chunk documents | `RecursiveCharacterTextSplitter`, `MarkdownHeaderTextSplitter` |
| **Embeddings** | Text → vectors | `OpenAIEmbeddings`, `AzureOpenAIEmbeddings`, `BedrockEmbeddings`, `HuggingFaceEmbeddings` |
| **Vector stores** | Store and search vectors | `Chroma`, `FAISS`, `PGVector`, `AzureSearch`, `OpenSearchVectorSearch`, `Pinecone`, `Qdrant` |
| **Retrievers** | `query → documents` interface | `vectorstore.as_retriever(search_kwargs={"k": 5})`, `EnsembleRetriever` (hybrid), `MultiQueryRetriever` |

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

docs = [Document(page_content=open("policy.txt").read(), metadata={"source": "IT Security Policy"})]
chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)

# vector_store = Chroma.from_documents(chunks, embedding=OpenAIEmbeddings())
# retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# Agentic RAG: give the agent a retrieval tool
# @tool
# def search_policies(query: str) -> str:
#     """Search Contoso policies. Use for any policy question."""
#     return "\n\n".join(d.page_content for d in retriever.invoke(query))
```

## 10. Memory

- **Short-term (conversation):** pass a `checkpointer` (e.g. `InMemorySaver`, or Postgres/Redis savers in production) to `create_agent`, and a `thread_id` in the config. The agent remembers the thread's history.
- **Long-term (across threads):** a LangGraph **Store** (`InMemoryStore`, Postgres store) for user preferences and facts.
- **Long conversations:** `SummarizationMiddleware` keeps the context small.

```python
agent = create_agent(model="anthropic:claude-sonnet-5-5", tools=[], checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "user-jane"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Jane."}]}, cfg)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, cfg)   # → "Jane"
```

## 11. Azure and AWS

```python
# Azure OpenAI (Microsoft Foundry):  pip install langchain-openai
from langchain_openai import AzureChatOpenAI
llm = AzureChatOpenAI(azure_deployment="gpt-4o-mini", api_version="2024-10-21")   # reads AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY
# Prefer keyless auth: azure_ad_token_provider from azure-identity (DefaultAzureCredential)

# Amazon Bedrock:  pip install langchain-aws
from langchain_aws import ChatBedrockConverse
llm = ChatBedrockConverse(model="<bedrock-model-id>", region_name="us-east-1")    # uses your AWS credentials / IAM role
```

Vector stores: `AzureSearch` (Azure AI Search), `OpenSearchVectorSearch`, and an `AmazonKnowledgeBasesRetriever` for Bedrock Knowledge Bases.

## 12. LangSmith

Set these environment variables to trace every run (prompts, tool calls, tokens, latency, errors):
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your key>
```
It also provides **datasets and evaluators** (offline evaluation), prompt versioning, and production monitoring. Open-source alternatives: **Langfuse**, Arize Phoenix, OpenTelemetry.

## 13. LangChain vs LlamaIndex vs Haystack

| | LangChain | LlamaIndex | Haystack |
|---|---|---|---|
| Focus | General LLM apps and **agents** | **Data/RAG**: indexing, retrieval, query engines | Production **search and RAG pipelines** |
| Strength | Integrations, `create_agent`, LangGraph | Advanced indexing, document parsing (LlamaParse) | Explicit pipelines, enterprise search |
| Pick when | Agents and broad integrations | RAG over complex documents is the core | You want clear, typed pipeline components |

They can be combined, for example LlamaIndex retrieval inside a LangGraph agent.

---

## 💬 Interview questions & answers

**Q1. What problem does LangChain solve?**
It gives standard interfaces for models, tools, retrievers and agents across hundreds of providers, so you build once and swap components. Since v1 it also offers `create_agent` with middleware, running on the LangGraph runtime.

**Q2. Chain vs agent?**
A chain is a fixed sequence you define (prompt → model → parser). An agent lets the model decide which tools to call and when, in a loop, until the goal is met.

**Q3. What is LCEL?**
LangChain Expression Language: composing runnables with `|`. Every component shares `invoke/stream/batch` (and async versions), which gives streaming, batching, retries and fallbacks for free.

**Q4. What does middleware add in LangChain 1.0?**
Hooks around model and tool calls to add behaviour without rewriting the agent: human approval, PII redaction, summarisation, call limits, retries, fallbacks and custom logic.

**Q5. How do you get reliable JSON out of an LLM in LangChain?**
`model.with_structured_output(PydanticModel)` or `create_agent(..., response_format=PydanticModel)`. It uses the provider's native structured output or tool calling, and validates the result.

**Q6. How do you add memory to a LangChain agent?**
Pass a checkpointer (persisted per `thread_id`) for conversation memory, and a Store for long-term memory across threads. Summarisation middleware keeps the context small.

**Q7. When would you use LangGraph instead of `create_agent`?**
When you need custom control flow: mixing deterministic and agentic steps, branching, parallel steps, multi-agent graphs, long-running durable workflows, or fine-grained human-in-the-loop.

---

## ✅ Final revision checklist

- [ ] I know the LangChain packages and what moved to `langchain-classic`.
- [ ] I can create a model with `init_chat_model` and use invoke/stream/batch.
- [ ] I can build an LCEL chain: prompt | model | parser.
- [ ] I can define a tool and build an agent with `create_agent`.
- [ ] I can add HITL, PII, summarisation and limit middleware.
- [ ] I can get structured output with Pydantic.
- [ ] I can name the RAG building blocks and the Azure/AWS integrations.
- [ ] I ran `code/langchain_agent.py`.

## 🔗 Official docs
- LangChain docs: https://docs.langchain.com/oss/python/langchain/overview
- LangChain 1.0 release notes: https://docs.langchain.com/oss/python/releases/langchain-v1
- LangSmith: https://docs.smith.langchain.com/

---
*My AI Engineering Study Notes* | [⬅ Previous](10-a2a.md) | [🏠 Home](../README.md) | [Next ➡](12-langgraph.md)
