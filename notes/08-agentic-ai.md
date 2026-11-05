# Agentic AI – Complete Developer Study Notes 🤖🛠️

> AI is moving from answering questions to taking actions. An agent is an LLM in a loop with tools, memory and a goal, plus the guardrails to keep it safe.

[⬅ Previous: Vector Databases](07-vector-databases-and-embeddings.md) | [🏠 Home](../README.md) | [Next: MCP ➡](09-mcp.md)

## 📚 What's covered

✅ [What an AI agent is](#1-what-an-ai-agent-is)
✅ [Agent architecture: model, tools, memory, planning](#2-agent-architecture)
✅ [The agent loop & ReAct](#3-the-agent-loop--react)
✅ [Workflows vs agents (and when NOT to build an agent)](#4-workflows-vs-agents)
✅ [Agent design patterns](#5-agent-design-patterns)
✅ [Multi-agent systems](#6-multi-agent-systems)
✅ [Memory: short-term, long-term, vector memory](#7-memory)
✅ [Tools & how agents connect to them (function calling, MCP, A2A)](#8-tools--interoperability)
✅ [Frameworks & platforms](#9-frameworks--platforms)
✅ [Security & guardrails](#10-security--guardrails)
✅ [Evaluation & observability](#11-evaluation--observability)
✅ [Production deployment & cost](#12-production--cost)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** AI engineers, GenAI developers, and agentic AI builders.

---

## 1. What an AI agent is

**An AI agent** = a system where an LLM **decides** what to do next to achieve a goal: it plans, calls tools, observes the results and repeats until done.

| Chatbot | Agent |
|---|---|
| Answers one message | Pursues a goal over many steps |
| Uses only its context | Calls tools: APIs, databases, code, browsers, other agents |
| Stateless or simple history | Memory and state |
| "Here's how to reset your password" | *Verifies the user, resets the password, emails a link, closes the ticket* |

**Key characteristics:** autonomy (to a set level), goal orientation, tool use, memory, planning and reflection.

## 2. Agent architecture

```
                 ┌────────────── Agent ───────────────┐
 Goal / user ──► │  LLM (reasoning + decisions)        │
                 │   ├── Instructions (role, rules)     │
                 │   ├── Planning (decompose, reflect)  │ ──► Tools: APIs, DBs, search, code, MCP servers
                 │   ├── Memory (short + long term)     │ ◄── Observations / results
                 │   └── Guardrails (policies, limits)  │ ──► Other agents (A2A)
                 └─────────────────────────────────────┘
                                 │
                                 ▼  answer / action / handoff to a human
```

## 3. The agent loop & ReAct

**ReAct = Reason + Act.** The model alternates between thinking, acting and observing:

```
Thought:     The user wants their ticket status. I need the ticket ID.
Action:      search_tickets(user="jane@contoso.com")
Observation: [{"id": 1042, "status": "in progress"}]
Thought:     I have the status.
Answer:      Ticket #1042 is in progress.
```

The loop in code (simplified sketch; `llm`, `run_tool` and `tool_result` stand for your model client and tool code):
```python
def run_agent(llm, tools, system, user_goal, max_steps=8):
    messages = [system, user_goal]
    for step in range(max_steps):                    # always cap the steps
        reply = llm(messages, tools=tools)
        if not reply.tool_calls:
            return reply.text                        # done: the model answered
        messages.append(reply)
        for call in reply.tool_calls:
            result = run_tool(call.name, call.args)  # YOUR code executes, with permission checks
            messages.append(tool_result(call.id, result))
    raise RuntimeError("Step limit reached - escalate to a human")
```
See a real, runnable version in [`code/langchain_agent.py`](../code/langchain_agent.py).

## 4. Workflows vs agents

| | Workflow (deterministic) | Agent (autonomous) |
|---|---|---|
| Control flow | Written by you in code | Chosen by the LLM |
| Predictability | High | Lower |
| Cost & latency | Lower | Higher (more LLM calls) |
| Best for | Known, repeatable steps | Open-ended problems where steps can't be predicted |

💡 **Start with the simplest thing that works:** a single LLM call → a workflow (prompt chaining, routing) → an agent only when the path truly can't be predefined. Many "agents" in production are well-designed workflows with one agentic step.

## 5. Agent design patterns

| Pattern | How it works | Use |
|---|---|---|
| **Prompt chaining** | Fixed sequence of LLM steps | Extract → validate → write |
| **Routing** | Classify input → send to a specialised handler | Support triage |
| **Parallelisation** | Run sub-tasks or voters in parallel, then combine | Speed, more reliable answers |
| **Orchestrator–workers** | A lead LLM splits the task and delegates to workers | Research, coding across files |
| **Evaluator–optimizer (reflection)** | One LLM drafts, another critiques; loop | Writing, code quality |
| **Plan-and-execute** | Make a plan first, then execute steps; re-plan on failure | Long tasks |
| **Tool-use (ReAct) agent** | Loop of think → act → observe | General agents |
| **Human-in-the-loop** | Pause for approval on risky steps | Payments, deletions, emails |

## 6. Multi-agent systems

| Architecture | Description | Example |
|---|---|---|
| **Supervisor** | One manager agent delegates to specialist agents | Supervisor → billing agent, tech agent, HR agent |
| **Hierarchical** | Supervisors of supervisors | Large enterprise processes |
| **Network / peer-to-peer** | Agents hand off to each other | Customer journey handoffs |
| **Sequential pipeline** | Agent A's output feeds agent B | Research → write → review |

**When multi-agent helps:** separate expertise, separate permissions and tools, parallel work, different models per role.
**When it hurts:** more cost, latency and failure points, plus hard debugging. Don't split what one agent with good tools can do.

## 7. Memory

| Memory | Holds | Implementation |
|---|---|---|
| **Short-term (working)** | Current conversation and task state | Message history, graph state (LangGraph), summarisation when long |
| **Long-term** | Facts across sessions: user preferences, past outcomes | Database or key-value store, LangGraph Store, Bedrock AgentCore Memory, Foundry Agent Service threads |
| **Semantic / vector memory** | Searchable past knowledge | Embeddings in a vector DB |
| **Episodic** | Records of past tasks and what worked | Logs plus retrieval |
| **Procedural** | How to do things | Instructions, skills, prompts |

Memory risks: storing PII, stale facts, and memory poisoning (an attacker plants false "facts"). Apply retention rules and review.

## 8. Tools & interoperability

| Mechanism | What it connects | Note |
|---|---|---|
| **Function / tool calling** | One app's LLM → its own functions | Built into every major model API |
| **MCP** (Model Context Protocol) | **Agent → tools and data**, via a standard server | Write a tool server once, use it from any MCP host ([note 09](09-mcp.md)) |
| **A2A** (Agent2Agent) | **Agent → another agent** (possibly another vendor's) | Delegate tasks between opaque agents ([note 10](10-a2a.md)) |
| **OpenAPI tools** | Agent → existing REST APIs | Foundry Agent Service and Bedrock Agents support OpenAPI specs |

**Good tool design:** clear names and descriptions (the LLM reads them!), simple typed parameters, informative error messages, idempotency for retries, least-privilege credentials, and confirmation for destructive actions.

## 9. Frameworks & platforms

| Framework / platform | Strength |
|---|---|
| **LangChain** (`create_agent`) | Fastest way to a standard tool-calling agent; middleware ([note 11](11-langchain.md)) |
| **LangGraph** | Low-level control: graphs, state, durable execution, human-in-the-loop ([note 12](12-langgraph.md)) |
| **CrewAI** | Role-based "crews" of agents |
| **AutoGen / Microsoft Agent Framework** | Multi-agent conversations; Microsoft's agent SDK |
| **Semantic Kernel** | Microsoft's SDK for .NET/Python/Java enterprise apps |
| **LlamaIndex** | Data/RAG-centric agents |
| **OpenAI Agents SDK, Claude Agent SDK, Google ADK, Strands Agents (AWS)** | Vendor agent SDKs |
| **Microsoft Foundry Agent Service** | Managed agents on Azure: tools, threads, evaluation, publishing to Teams/M365 ([note 13](13-azure-ai-services.md)) |
| **Amazon Bedrock Agents / Bedrock AgentCore** | Managed agents on AWS; AgentCore runs agents from any framework ([note 14](14-aws-ai-services.md)) |

## 10. Security & guardrails

| Risk | Mitigation |
|---|---|
| **Prompt injection** (direct and indirect via tool results/web pages) | Treat tool output as data, isolate untrusted content, input/output filters, least-privilege tools |
| **Excessive agency** | Limit tools and permissions; human approval for high-impact actions; spending/step limits |
| **Tool misuse / data exfiltration** | Allow-lists, egress controls, scoped OAuth tokens, audit logs |
| **Runaway loops & cost** | Max steps, timeouts, token budgets, circuit breakers |
| **Identity confusion** | Agents act **on behalf of** a user with that user's permissions (OAuth on-behalf-of, Entra Agent ID, AgentCore Identity) |
| **Memory poisoning** | Validate what goes into long-term memory |
| **Harmful content** | Azure AI Content Safety, Bedrock Guardrails, model safety settings |

Frameworks to cite: **OWASP Top 10 for LLM Applications** and OWASP's agentic AI threat guidance.

## 11. Evaluation & observability

| Evaluate | Metric |
|---|---|
| Task success | Did it achieve the goal? (end-to-end tests with expected outcomes) |
| Tool use | Right tool? Right arguments? Unnecessary calls? |
| Trajectory | Was the path efficient and safe? |
| Groundedness | Are claims supported by tool results? |
| Safety | Policy violations, injection resistance (red-teaming) |
| Efficiency | Steps, tokens, latency and cost per task |

**Observability:** trace every LLM call, tool call, input/output, latency and token count (OpenTelemetry, LangSmith, Langfuse, Foundry tracing, AgentCore Observability, CloudWatch, Application Insights).

## 12. Production & cost

- Containerise the agent; deploy on a managed runtime (Foundry Agent Service, Bedrock AgentCore Runtime) or containers (Azure Container Apps, AKS, ECS, EKS, Lambda for short tasks).
- **Durable execution** for long tasks (LangGraph checkpointers, queues), so a crash doesn't restart the job.
- Version prompts, tools and models; run evaluations in CI before release.
- Cost control: smaller models for routine steps, caching, step limits, parallel tool calls, summarised memory.

---

## 💬 Interview questions & answers

**Q1. What makes something an agent rather than a chatbot?**
The LLM controls the flow: it decides which tools to call and in what order, observes results and iterates toward a goal, with memory and some autonomy.

**Q2. Single agent with tools or a multi-agent system?**
Start with a single agent with well-designed tools. It's cheaper, faster and easier to debug. Move to multi-agent when you need separate expertise, permissions or parallelism, or the toolset is too large for one agent to choose well.

**Q3. Explain ReAct.**
The model interleaves reasoning ("I need X") with actions (tool calls) and observations (tool results) in a loop until it can answer. It makes tool use explicit and debuggable.

**Q4. How do you stop an agent from doing something dangerous?**
Least-privilege tools, allow-lists, human-in-the-loop approval for high-impact actions, step/token/spend limits, input and output guardrails, sandboxed code execution, and audit logging.

**Q5. How do you evaluate an agent?**
End-to-end task success on test scenarios, tool-selection and argument accuracy, trajectory efficiency, groundedness, safety red-teaming, and cost/latency per task, all traced in production.

**Q6. MCP vs A2A?**
MCP standardises how an agent connects to tools and data (agent-to-tool). A2A standardises how independent agents discover each other and delegate tasks (agent-to-agent). They complement each other.

**Q7. How do agents handle long-running tasks?**
With persisted state (checkpoints), resumable execution, asynchronous jobs and notifications, and human approval steps that can wait hours or days.

---

## ✅ Final revision checklist

- [ ] I can draw an agent architecture (LLM, tools, memory, planning, guardrails).
- [ ] I can write the agent loop in pseudocode, with a step limit.
- [ ] I can explain when a workflow beats an agent.
- [ ] I know six agent design patterns and three multi-agent architectures.
- [ ] I can explain short-term vs long-term memory.
- [ ] I can compare function calling, MCP and A2A.
- [ ] I know six agent security risks and their mitigations.
- [ ] I can name managed agent platforms on Azure and AWS.

## 🔗 Official docs
- Anthropic, "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents
- OWASP GenAI Security Project: https://genai.owasp.org/
- Microsoft Foundry Agent Service: https://learn.microsoft.com/azure/ai-foundry/agents/overview
- Amazon Bedrock AgentCore: https://aws.amazon.com/bedrock/agentcore/

---
*My AI Engineering Study Notes* | [⬅ Previous](07-vector-databases-and-embeddings.md) | [🏠 Home](../README.md) | [Next ➡](09-mcp.md)
