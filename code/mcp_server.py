"""A small MCP server (MCP Python SDK v2): IT helpdesk tools + a policy resource + a prompt.

Run it locally over stdio (how desktop hosts such as Claude Desktop or VS Code launch it):
    python mcp_server.py
Or over Streamable HTTP (for remote clients), served at http://localhost:8000/mcp:
    python mcp_server.py --http
Inspect it interactively:
    mcp dev mcp_server.py           # needs: pip install "mcp[cli]"
"""
import sys

from pydantic import BaseModel

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("contoso-helpdesk", log_level="WARNING")   # quieter logs; use "INFO" or "DEBUG" when debugging


class Ticket(BaseModel):
    id: int
    title: str
    priority: str
    status: str


TICKETS: dict[int, Ticket] = {}


@mcp.tool()
def create_ticket(title: str, priority: str = "medium") -> Ticket:
    """Create an IT support ticket. priority must be low, medium or high."""
    if priority not in {"low", "medium", "high"}:
        raise ToolError("priority must be low, medium or high")   # expected error: shown to the model
    ticket = Ticket(id=len(TICKETS) + 1, title=title, priority=priority, status="open")
    TICKETS[ticket.id] = ticket
    return ticket


@mcp.tool()
def get_ticket(ticket_id: int) -> Ticket:
    """Look up an IT support ticket by its id."""
    if ticket_id not in TICKETS:
        raise ToolError(f"ticket {ticket_id} not found")
    return TICKETS[ticket_id]


@mcp.resource("policy://password")
def password_policy() -> str:
    """Contoso's device password policy."""
    return "Minimum 12 characters; upper, lower, numbers and symbols; change every 90 days."


@mcp.prompt()
def triage(issue: str) -> str:
    """Prompt template for triaging a user's IT issue."""
    return f"Classify this IT issue as hardware, software, access or network, then suggest a priority:\n{issue}"


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
