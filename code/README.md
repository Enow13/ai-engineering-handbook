# 💻 Runnable code examples

All examples run **offline, with no API keys**, so every student can run them. Each one was tested with Python 3.13 and the package versions in [`../requirements.txt`](../requirements.txt).

## Setup (once)

```bash
# from the repository root
python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
cd code
```

## Examples

| Run | What you'll see | Read with |
|---|---|---|
| `python rag_minimal.py "How long must my password be?"` | The retrieved chunk with its score, then the grounded prompt | [06 RAG](../notes/06-rag.md) |
| `python rag_minimal.py "parental leave policy"` | **No context found**: the relevance threshold stops irrelevant chunks | [06 RAG](../notes/06-rag.md) |
| `python mcp_client.py` | The client starts the MCP server, lists its tools, creates a ticket, gets an error back for bad input, reads a resource and a prompt | [09 MCP](../notes/09-mcp.md) |
| `python mcp_server.py --http` | Serves MCP over Streamable HTTP at `http://localhost:8000/mcp` (Ctrl+C to stop) | [09 MCP](../notes/09-mcp.md) |
| `mcp dev mcp_server.py` | Opens the **MCP Inspector** in your browser to call tools by hand (needs Node.js) | [09 MCP](../notes/09-mcp.md) |
| `python langchain_agent.py` | The agent loop: Human → AI tool call → Tool result → AI answer | [11 LangChain](../notes/11-langchain.md) |
| `python langgraph_workflow.py` | The graph pauses for human approval, resumes, and routes a second request differently | [12 LangGraph](../notes/12-langgraph.md) |

## Use a real model (optional)

`langchain_agent.py` uses a scripted stand-in model by default. To use a real model:
```bash
pip install langchain-anthropic
export ANTHROPIC_API_KEY=<your key>              # PowerShell: $env:ANTHROPIC_API_KEY="<your key>"
export MODEL=anthropic:claude-sonnet-5-5         # PowerShell: $env:MODEL="anthropic:claude-sonnet-5-5"
python langchain_agent.py
```
Never commit API keys. Use environment variables or a `.env` file (already in `.gitignore`).

## Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment, then `pip install -r requirements.txt` (from the repo root) |
| `No module named 'mcp.server.fastmcp'` | You're following an older MCP tutorial. SDK v2 uses `from mcp.server import MCPServer` |
| `python: command not found` | Use `python3` (macOS/Linux) or `py` (Windows) |
| `requires a different Python` | Install Python 3.10 or newer |
| `Address already in use` (port 8000) | Another server is running; stop it, or close the old terminal |
