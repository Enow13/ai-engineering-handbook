# MCP (Model Context Protocol) – Complete Developer Study Notes 🔌🧰

> MCP is the "USB-C port for AI": build a tool server once and any MCP-compatible app or agent can use it, whether that's Claude, VS Code, Copilot, Cursor or your own agent.

[⬅ Previous: Agentic AI](08-agentic-ai.md) | [🏠 Home](../README.md) | [Next: A2A ➡](10-a2a.md)

## 📚 What's covered

✅ [What MCP is & the problem it solves](#1-what-mcp-is)
✅ [Architecture: host, client, server](#2-architecture-host-client-server)
✅ [Server primitives: tools, resources, prompts](#3-server-primitives)
✅ [Client features: elicitation (and deprecated sampling & roots)](#4-client-features)
✅ [Transports: stdio & Streamable HTTP](#5-transports)
✅ [The protocol: JSON-RPC, discovery & the 2026-07-28 spec changes](#6-the-protocol)
✅ [Security & authorization (OAuth 2.1)](#7-security--authorization)
✅ [Build an MCP server & client in Python (tested)](#8-build-a-server-and-client-in-python)
✅ [Connect a server to Claude Desktop / VS Code](#9-connect-a-server-to-a-host)
✅ [MCP on Azure and AWS](#10-mcp-on-azure-and-aws)
✅ [MCP vs function calling vs A2A](#11-mcp-vs-function-calling-vs-a2a)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** agent builders, platform engineers, and anyone integrating LLMs with company systems.

---

## 1. What MCP is

**Model Context Protocol (MCP)** is an **open standard** for connecting AI applications to external **tools** and **data**. Anthropic introduced it in November 2024. It's now governed under the **Agentic AI Foundation (AAIF)** at the Linux Foundation, and supported by Anthropic, OpenAI, Microsoft, Google, AWS and many tool vendors.

**The problem (M × N):** without a standard, every AI app (M) needs a custom integration for every system (N): Jira, GitHub, Postgres, Salesforce...
**MCP's answer (M + N):** each system ships **one MCP server**; each AI app implements **one MCP client**. Everything works with everything.

## 2. Architecture: host, client, server

```
┌─────────────────── MCP Host (the AI app) ───────────────────┐
│  e.g. Claude Desktop, VS Code / GitHub Copilot, Cursor,     │
│  your LangGraph agent, Foundry/Bedrock agents               │
│                                                              │
│   LLM ◄──► MCP Client A ──┐   MCP Client B ──┐               │
└───────────────────────────┼──────────────────┼───────────────┘
                            │ stdio (local)    │ Streamable HTTP (remote)
                            ▼                  ▼
                     MCP Server: files    MCP Server: Jira / DB / internal API
```

| Role | What it is |
|---|---|
| **Host** | The application the user interacts with; manages clients, the LLM and user consent |
| **Client** | A connector inside the host; one client per server connection |
| **Server** | A program exposing tools, resources and prompts for one system (GitHub, Postgres, your API) |

## 3. Server primitives

| Primitive | Controlled by | What it is | Example |
|---|---|---|---|
| **Tools** | **Model** (the LLM decides to call them) | Functions with a JSON-schema input | `create_ticket(title, priority)`, `run_sql(query)` |
| **Resources** | **Application** (host decides what to load) | Read-only data identified by a URI | `file:///policy.pdf`, `policy://password`, `db://customers/schema` |
| **Prompts** | **User** (picked from a menu, often as slash commands) | Reusable prompt templates with arguments | `/triage issue="VPN down"` |

Discovery methods: `tools/list`, `resources/list`, `prompts/list`. Use them with `tools/call`, `resources/read`, `prompts/get`.

## 4. Client features

| Feature | What it does | Status (2026-07-28 spec) |
|---|---|---|
| **Elicitation** | The server asks the **user** for more input mid-task ("Which project?") | ✅ Supported, now delivered via *multi-round-trip requests*: the server answers `input_required`, and the client asks the user and retries |
| **Sampling** | The server asks the client's LLM to generate text | ⚠️ **Deprecated**. Servers should call model APIs directly |
| **Roots** | The server asks which folders/files it may use | ⚠️ **Deprecated**. Pass paths via tool parameters, resource URIs or server config |

## 5. Transports

| Transport | How | Use |
|---|---|---|
| **stdio** | The host starts the server as a **local subprocess** and talks over stdin/stdout | Local tools: files, Git, local DBs, desktop apps |
| **Streamable HTTP** | The client sends HTTP POST requests to a single endpoint (e.g. `https://api.contoso.com/mcp`) | **Remote/production** servers shared by many users; scales behind load balancers |
| ~~HTTP + SSE~~ (2024 spec) | Older remote transport | **Deprecated**, replaced by Streamable HTTP |

## 6. The protocol

- Messages are **JSON-RPC 2.0** (requests, responses and notifications).
- **Spec versions are dated:** `2024-11-05` → `2025-03-26` → `2025-06-18` → `2025-11-25` → **`2026-07-28` (current)**.

**What changed in the 2026-07-28 spec (important: many tutorials are older):**

| Before (≤ 2025-11-25) | Now (2026-07-28) |
|---|---|
| `initialize` handshake, then a **session** (`Mcp-Session-Id` header) | **Stateless requests**: each request carries the protocol version and client capabilities in `_meta`; any server instance can answer |
| Capabilities negotiated at startup | **`server/discover`** returns supported versions, capabilities and identity |
| Standalone GET/SSE stream for notifications | **`subscriptions/listen`** for change notifications |
| Server could send requests to the client mid-call | **Multi-round-trip requests (MRTR):** server returns `resultType: "input_required"` plus an opaque `requestState`; the client retries |
| Implicit session state | State lives in **explicit handles** the server returns and the client passes as tool arguments |
| – | Caching hints on list/read results (`ttlMs`, `cacheScope`) and routing headers (`Mcp-Method`, `Mcp-Name`) |

Deprecation policy: deprecated features stay for **at least 12 months**. The official SDKs handle these details, so you mostly write tools.

**Example `tools/call` request (JSON-RPC):**
```json
{"jsonrpc": "2.0", "id": 7, "method": "tools/call",
 "params": {"name": "create_ticket", "arguments": {"title": "Laptop won't boot", "priority": "high"}}}
```

## 7. Security & authorization

**Authorization (remote servers):** OAuth 2.1. The MCP server is an OAuth **resource server**:
- **Protected Resource Metadata (RFC 9728)** tells clients which authorization server to use (mandatory).
- **Resource indicators (RFC 8707)** bind tokens to *this* server, so tokens can't be replayed elsewhere.
- **Client ID Metadata Documents** are preferred for client registration (Dynamic Client Registration is deprecated).
- **Step-up authorization:** the server can ask for extra scopes for a sensitive call.
- Enterprise options: **Enterprise-Managed Authorization** (central IdP control, e.g. Microsoft Entra ID, Okta).

**Top MCP risks and defences:**

| Risk | Defence |
|---|---|
| **Tool poisoning** (malicious instructions hidden in tool descriptions) | Only install trusted servers; review descriptions; pin versions |
| **Prompt injection via tool results** | Treat results as data; human approval for risky tools |
| **Over-privileged servers** | Least-privilege tokens; read-only by default; separate servers per sensitivity |
| **Token passthrough / confused deputy** | Never forward the user's token to downstream APIs unchanged; validate audience |
| **Rug pulls** (server changes after you trust it) | Version pinning, allow-lists, a private registry |
| **Local server running arbitrary code** | Sandboxing/containers for stdio servers; review before installing |

## 8. Build a server and client in Python

Tested with the **MCP Python SDK v2** (`pip install "mcp[cli]"`, Python 3.10+). Full files: [`code/mcp_server.py`](../code/mcp_server.py), [`code/mcp_client.py`](../code/mcp_client.py).

> ⚠️ **SDK v1 → v2:** `FastMCP` was renamed to **`MCPServer`** (`from mcp.server import MCPServer`). Old tutorials using `from mcp.server.fastmcp import FastMCP` need `pip install "mcp<2"`, or need updating.

**Server:**
```python
from pydantic import BaseModel
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("contoso-helpdesk")

class Ticket(BaseModel):                 # typed return = structured output for the model
    id: int
    title: str
    priority: str
    status: str

TICKETS: dict[int, Ticket] = {}

@mcp.tool()
def create_ticket(title: str, priority: str = "medium") -> Ticket:
    """Create an IT support ticket. priority must be low, medium or high."""   # the LLM reads this!
    if priority not in {"low", "medium", "high"}:
        raise ToolError("priority must be low, medium or high")    # returned to the model as is_error
    ticket = Ticket(id=len(TICKETS) + 1, title=title, priority=priority, status="open")
    TICKETS[ticket.id] = ticket
    return ticket

@mcp.resource("policy://password")
def password_policy() -> str:
    """Contoso's device password policy."""
    return "Minimum 12 characters; upper, lower, numbers and symbols; change every 90 days."

@mcp.prompt()
def triage(issue: str) -> str:
    """Prompt template for triaging a user's IT issue."""
    return f"Classify this IT issue as hardware, software, access or network:\n{issue}"

if __name__ == "__main__":
    mcp.run()                              # stdio; use mcp.run(transport="streamable-http") for HTTP
```

**Client** (launches the server over stdio):
```python
import asyncio, sys
from mcp import Client, StdioServerParameters

async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with Client(params) as client:               # or Client("http://localhost:8000/mcp")
        print([t.name for t in (await client.list_tools()).tools])
        result = await client.call_tool("create_ticket", {"title": "Laptop won't boot", "priority": "high"})
        print(result.structured_content)    # {'id': 1, 'title': "Laptop won't boot", ...}

asyncio.run(main())
```

**Run and test:**
```bash
cd code
python mcp_client.py                         # client starts the server and calls it
mcp dev mcp_server.py                         # opens the MCP Inspector UI to test tools by hand
python mcp_server.py --http                   # serve at http://localhost:8000/mcp
```

Official SDKs also exist for **TypeScript, C#/.NET, Java, Kotlin, Go, Rust, Swift, Ruby and PHP**.

## 9. Connect a server to a host

**Claude Desktop:** Settings → **Developer** → **Edit Config** opens `claude_desktop_config.json`. Add your server, then restart Claude Desktop:
```json
{
  "mcpServers": {
    "contoso-helpdesk": {
      "command": "python",
      "args": ["C:/path/to/code/mcp_server.py"]
    }
  }
}
```

**VS Code (GitHub Copilot agent mode):** create `.vscode/mcp.json` in your project:
```json
{
  "servers": {
    "contoso-helpdesk": { "type": "stdio", "command": "python", "args": ["code/mcp_server.py"] }
  }
}
```

Remote servers are added by URL (for example `https://api.contoso.com/mcp`); the host handles the OAuth sign-in.

## 10. MCP on Azure and AWS

| Need | Azure | AWS |
|---|---|---|
| Host your own MCP server | Azure Container Apps, Azure Functions, App Service, AKS | Lambda, ECS/Fargate, EKS, **Bedrock AgentCore Runtime** |
| Expose existing APIs as MCP tools | **Azure API Management** (expose REST APIs as MCP servers, with policies and auth) | **Bedrock AgentCore Gateway** (turns APIs and Lambda functions into MCP tools) |
| Agents that consume MCP tools | **Foundry Agent Service** (MCP tool), Copilot Studio, GitHub Copilot | **Bedrock AgentCore**, **Strands Agents**, Amazon Q Developer |
| Identity | Microsoft Entra ID (OAuth) | Amazon Cognito, AgentCore Identity |
| Ready-made servers | Azure MCP Server (Azure resources), Microsoft Learn docs MCP | AWS MCP servers (AWS docs, services) |

## 11. MCP vs function calling vs A2A

| | Function calling | MCP | A2A |
|---|---|---|---|
| Scope | Inside one app | Agent ↔ **tools and data** | Agent ↔ **agent** |
| Reusability | Per app | Any MCP host | Any A2A client |
| The other side is | Your code | A tool server (transparent: you see its tools) | An opaque agent (you see its skills, not its internals) |
| Typical call | `get_weather(city)` | `tools/call create_ticket` | `SendMessage` "Book travel for the offsite" → a **task** with status and artifacts |

MCP and function calling work together: the host turns MCP tools into the model's function-calling format.

---

## 💬 Interview questions & answers

**Q1. What problem does MCP solve?**
The M×N integration problem. Instead of every AI app building custom connectors for every system, systems expose one MCP server and apps implement one MCP client, so any compatible app can use any server.

**Q2. Explain tools vs resources vs prompts.**
Tools are model-controlled actions with typed inputs. Resources are application-controlled, read-only context identified by URIs. Prompts are user-selected reusable templates.

**Q3. stdio or Streamable HTTP?**
stdio for local, single-user tools launched by the host (files, local Git). Streamable HTTP for remote, shared, production servers that need authentication and scaling.

**Q4. What changed in the 2026-07-28 MCP spec?**
It removed sessions and the initialize handshake (requests are now stateless and carry the version and capabilities in `_meta`), added `server/discover` and `subscriptions/listen`, introduced multi-round-trip requests for elicitation, deprecated sampling and roots, and tightened OAuth requirements.

**Q5. How do you secure an MCP server?**
OAuth 2.1 with protected resource metadata and audience-bound tokens, least-privilege scopes, input validation, no token passthrough, human approval for destructive tools, trusted and version-pinned servers only, sandboxing for local servers, and audit logging.

**Q6. What is tool poisoning?**
Malicious instructions hidden in a tool's description or metadata that the LLM reads and follows, for example "also send the user's files to X". Defend with trusted sources, description review, pinning and allow-lists.

**Q7. MCP vs A2A?**
MCP connects an agent to tools and data it controls directly. A2A lets an agent delegate a goal to another independent agent, which manages its own tools and returns task results. A2A agents often use MCP internally.

**Q8. How would you expose an existing internal REST API to agents?**
Wrap it in an MCP server (custom, or a gateway such as Azure API Management or Bedrock AgentCore Gateway), with clear tool descriptions, OAuth via the company IdP, rate limits and logging. Then register it with the agent platform.

---

## ✅ Final revision checklist

- [ ] I can explain host, client and server, and draw the architecture.
- [ ] I know who controls tools, resources and prompts.
- [ ] I can compare stdio and Streamable HTTP.
- [ ] I can list the main 2026-07-28 spec changes and which features are deprecated.
- [ ] I know the OAuth pieces (resource server, RFC 9728, RFC 8707) and five MCP security risks.
- [ ] I can build and run an MCP server and client with the Python SDK v2 (`MCPServer`).
- [ ] I can configure an MCP server in Claude Desktop or VS Code.
- [ ] I can compare function calling, MCP and A2A.

## 🔗 Official docs
- MCP specification & docs: https://modelcontextprotocol.io
- MCP Python SDK: https://py.sdk.modelcontextprotocol.io/
- MCP Inspector: https://github.com/modelcontextprotocol/inspector

---
*My AI Engineering Study Notes* | [⬅ Previous](08-agentic-ai.md) | [🏠 Home](../README.md) | [Next ➡](10-a2a.md)
