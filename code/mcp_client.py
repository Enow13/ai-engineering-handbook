"""MCP client (MCP Python SDK v2): launches mcp_server.py over stdio, then discovers and uses it.

Run (from the code/ folder):
    python mcp_client.py
To connect to a remote server instead, pass its URL: Client("http://localhost:8000/mcp")
"""
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

SERVER = Path(__file__).with_name("mcp_server.py")


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with Client(params) as client:
        # 1. Discover what the server offers
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools.tools])

        # 2. Call a tool (an LLM would choose this call and its arguments)
        created = await client.call_tool("create_ticket", {"title": "Laptop won't boot", "priority": "high"})
        print("create_ticket ->", created.structured_content)

        # 3. Errors come back as results with is_error=True, so the model can correct itself
        bad = await client.call_tool("create_ticket", {"title": "Printer", "priority": "urgent"})
        print("Invalid call -> is_error:", bad.is_error, "|", bad.content[0].text)

        # 4. Read a resource (context for the model)
        policy = await client.read_resource("policy://password")
        print("Resource ->", policy.contents[0].text)

        # 5. Get a prompt template
        prompt = await client.get_prompt("triage", {"issue": "VPN disconnects every hour"})
        print("Prompt ->", prompt.messages[0].content.text[:60], "...")


if __name__ == "__main__":
    asyncio.run(main())
