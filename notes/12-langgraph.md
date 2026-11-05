# LangGraph – Complete Developer Study Notes 🕸️🤖

> When an agent needs to be reliable (approvals, retries, branching, long-running steps, many agents), you draw it as a graph. LangGraph is the runtime for that.

[⬅ Previous: LangChain](11-langchain.md) | [🏠 Home](../README.md) | [Next: Azure AI Services ➡](13-azure-ai-services.md)

## 📚 What's covered

✅ [What LangGraph is & when to use it](#1-what-langgraph-is)
✅ [Core concepts: State, Nodes, Edges, Reducers](#2-core-concepts)
✅ [Your first graph](#3-your-first-graph)
✅ [Conditional edges & routing](#4-conditional-edges--routing)
✅ [A tool-calling agent as a graph](#5-a-tool-calling-agent-as-a-graph)
✅ [Persistence: checkpointers & threads](#6-persistence-checkpointers--threads)
✅ [Human-in-the-loop with `interrupt`](#7-human-in-the-loop)
✅ [Long-term memory (Store)](#8-long-term-memory-store)
✅ [Streaming](#9-streaming)
✅ [Multi-agent patterns: supervisor, handoffs, subgraphs](#10-multi-agent-patterns)
✅ [Parallelism (fan-out / map-reduce)](#11-parallelism)
✅ [Deployment](#12-deployment)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** agent engineers building production workflows and multi-agent systems.

---

## 1. What LangGraph is

**LangGraph** is a low-level, open-source framework and runtime for building **stateful, controllable** agents and workflows as **graphs**. It reached v1.0 in October 2025. LangChain's `create_agent` runs on it.

**Key features:** durable execution (resume after crashes), built-in persistence, human-in-the-loop, streaming, memory, subgraphs, and support for cycles (loops), which simple DAG pipelines can't do.

| Use **LangChain `create_agent`** | Use **LangGraph** |
|---|---|
| Standard tool-calling agent | Custom control flow, mixing fixed steps with agentic steps |
| Quick to build | Long-running, durable business processes |
| Middleware is enough | Multi-agent systems, parallel branches, approvals at specific steps |

## 2. Core concepts

| Concept | What it is |
|---|---|
| **State** | A shared data structure (TypedDict or Pydantic) that flows through the graph |
| **Node** | A Python function: takes the state, returns a **partial update** |
| **Edge** | Which node runs next (fixed) |
| **Conditional edge** | A function that picks the next node based on the state |
| **`START` / `END`** | Entry and exit points |
| **Reducer** | How updates merge into a state key (default: overwrite; `add_messages`: append) |
| **Checkpointer** | Saves state after every step → memory, resume, time-travel, HITL |
| **Thread** | One conversation/workflow instance (`thread_id`) |
| **Compile** | Turns the builder into a runnable graph (`invoke`, `stream`) |

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]   # reducer: append new messages instead of overwriting
    category: str                              # default: overwrite
```

`MessagesState` is a ready-made state with a `messages` key and the `add_messages` reducer.

## 3. Your first graph

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    summary: str

def summarize(state: State) -> dict:
    return {"summary": state["text"][:40] + "..."}     # in real apps: call an LLM

builder = StateGraph(State)
builder.add_node("summarize", summarize)
builder.add_edge(START, "summarize")
builder.add_edge("summarize", END)
graph = builder.compile()

print(graph.invoke({"text": "LangGraph lets you build reliable, stateful agents as graphs."}))
```

## 4. Conditional edges & routing

```python
from typing import Literal

def route(state: State) -> Literal["approval", "answer"]:
    return "approval" if state["category"] == "password_reset" else "answer"

builder.add_conditional_edges("classify", route)       # the return value names the next node
```

**Full runnable workflow:** [`code/langgraph_workflow.py`](../code/langgraph_workflow.py). It classifies an IT request, routes it, and pauses for **human approval** before a password reset.

```bash
cd code && python langgraph_workflow.py
# Paused for approval: {'question': "Approve password reset for: 'I forgot my password'?"}
# Category: password_reset | Approved: True
# Result: Password reset link sent to the user's registered email.
```

```
START → classify ─┬─(password_reset)→ approval ⏸ → reset_password → END
                  └─(general)──────→ answer ───────────────────────→ END
```

## 5. A tool-calling agent as a graph

The classic loop (what `create_agent` builds for you):

```python
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

tools = [get_ticket_status]                         # @tool functions
llm = model.bind_tools(tools)                       # any LangChain chat model

def call_model(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))          # executes the requested tool calls
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)   # tool calls? → "tools", else → END
builder.add_edge("tools", "agent")                  # loop back with the results
graph = builder.compile()
```

```
START → agent ──(tool calls)──► tools ──┐
          ▲                              │
          └──────────────────────────────┘
        agent ──(no tool calls)──► END
```

## 6. Persistence: checkpointers & threads

```python
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "customer-123"}}
graph.invoke({"messages": [("user", "Hi, I'm Jane")]}, config)
graph.invoke({"messages": [("user", "What's my name?")]}, config)   # remembers: same thread
```

| Checkpointer | Use |
|---|---|
| `InMemorySaver` | Learning, tests |
| `SqliteSaver` | Local apps |
| `PostgresSaver` | **Production** (`langgraph-checkpoint-postgres`) |
| Redis, MongoDB, cloud savers | Other production options |

What checkpoints give you: **conversation memory**, **fault tolerance** (resume from the last step), **human-in-the-loop**, and **time travel** (`graph.get_state_history(config)` to inspect or replay earlier states).

## 7. Human-in-the-loop

`interrupt()` pauses the graph, saves state, and returns a payload to your app. You resume with `Command(resume=...)`.

```python
from langgraph.types import interrupt, Command

def approval(state):
    decision = interrupt({"question": "Approve this refund of $500?"})   # pauses here
    return {"approved": decision == "yes"}

first = graph.invoke({"request": "Refund order 991"}, config)
print(first["__interrupt__"])                 # show this to a human (UI, Teams, email...)
final = graph.invoke(Command(resume="yes"), config)   # resumes exactly where it stopped
```

Common HITL patterns: **approve/reject** an action, **edit** tool arguments before they run, **review** an output, ask for **missing input**.

## 8. Long-term memory (Store)

Checkpointers remember *within* a thread. A **Store** remembers *across* threads (user profile, preferences, learned facts).

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("users", "jane"), "preferences", {"language": "French", "tone": "brief"})
item = store.get(("users", "jane"), "preferences")
print(item.value)                                  # {'language': 'French', 'tone': 'brief'}
graph = builder.compile(checkpointer=InMemorySaver(), store=store)   # nodes can read/write it
```

Stores can also be configured with an embedding index for **semantic search over memories**.

## 9. Streaming

```python
for chunk in graph.stream(inputs, config, stream_mode="updates"):   # node-by-node state updates
    print(chunk)
for msg, meta in graph.stream(inputs, config, stream_mode="messages"):  # LLM tokens as they're generated
    print(msg.content, end="")
```
Modes: `values` (full state after each step), `updates` (deltas), `messages` (tokens), `custom`, `debug`.

## 10. Multi-agent patterns

| Pattern | How in LangGraph |
|---|---|
| **Supervisor** | A supervisor node (LLM) routes to specialist agent nodes, which report back |
| **Handoffs** | An agent returns `Command(goto="other_agent", update={...})` to transfer control |
| **Hierarchical** | Supervisors of teams, built as **subgraphs** |
| **Subgraphs** | A compiled graph used as a node inside another graph (reuse, separation of concerns) |
| **Network (swarm)** | Agents hand off to each other freely |

Agents in a graph can also call external agents over **A2A**, and use tools from **MCP** servers ([notes 09–10](09-mcp.md)).

## 11. Parallelism

- **Fan-out:** add edges from one node to several nodes; they run in the same step (in parallel).
- **Map-reduce:** use `Send("worker", {"item": x})` from a conditional edge to launch a dynamic number of parallel workers, then collect their results with a reducer (e.g. `operator.add`).
- Use for: researching several sources at once, grading many documents, processing a batch of tickets.

## 12. Deployment

| Option | Notes |
|---|---|
| Your own API | Wrap `graph.invoke/stream` in **FastAPI**, containerise, use a Postgres checkpointer |
| **LangGraph Platform / LangSmith Deployment** | Managed hosting with task queues, persistence, streaming APIs, cron, and LangGraph Studio for visual debugging |
| Azure | Azure Container Apps / AKS + Azure Database for PostgreSQL; or connect to Foundry Agent Service |
| AWS | **Bedrock AgentCore Runtime** (framework-agnostic agent hosting), ECS/EKS/Lambda + Aurora PostgreSQL |

---

## 💬 Interview questions & answers

**Q1. What are nodes, edges and state in LangGraph?**
State is the shared data passed through the graph. Nodes are functions that read the state and return partial updates. Edges decide which node runs next, either fixed or conditional on the state.

**Q2. What is a reducer?**
A function that defines how a node's update merges into a state key. By default it overwrites; `add_messages` appends messages, and `operator.add` concatenates lists from parallel branches.

**Q3. What does a checkpointer give you?**
Persistence of state after each step per thread, which enables conversation memory, resuming after failures, human-in-the-loop pauses, and time-travel debugging.

**Q4. How do you implement human approval before a risky action?**
Put `interrupt()` in a node before the action (or use `HumanInTheLoopMiddleware` with `create_agent`), compile with a checkpointer, show the interrupt payload to a human, then resume with `Command(resume=decision)`.

**Q5. Checkpointer vs Store?**
A checkpointer saves state within one thread (short-term memory). A Store saves data across threads and users (long-term memory such as preferences), optionally with semantic search.

**Q6. How do you run steps in parallel?**
Fan-out edges for a fixed set of parallel nodes, or `Send` for dynamic map-reduce, with reducers to combine results.

**Q7. Why LangGraph over a simple while-loop agent?**
Durability (resume after crashes), built-in persistence and HITL, explicit and testable control flow, streaming, parallelism, subgraphs for multi-agent systems, and observability.

---

## ✅ Final revision checklist

- [ ] I can define State, Node, Edge, Conditional edge, Reducer, Checkpointer and Thread.
- [ ] I can build and compile a StateGraph with a conditional edge.
- [ ] I can draw the agent ↔ tools loop.
- [ ] I can add memory with a checkpointer and a `thread_id`.
- [ ] I can implement HITL with `interrupt` and `Command(resume=...)`.
- [ ] I can explain Store vs checkpointer.
- [ ] I can describe the supervisor and handoff multi-agent patterns.
- [ ] I ran `code/langgraph_workflow.py`.

## 🔗 Official docs
- LangGraph docs: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph v1 release notes: https://docs.langchain.com/oss/python/releases/langgraph-v1
- LangGraph Studio & Platform: https://docs.langchain.com/langsmith/home

---
*My AI Engineering Study Notes* | [⬅ Previous](11-langchain.md) | [🏠 Home](../README.md) | [Next ➡](13-azure-ai-services.md)
