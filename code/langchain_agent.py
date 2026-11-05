"""LangChain 1.x agent with tools (create_agent).

Runs WITHOUT an API key using a scripted stand-in model, so you can see the agent loop.
To use a real model, set an env var and a provider package, for example:
    pip install langchain-anthropic   and   export ANTHROPIC_API_KEY=...   and   export MODEL=anthropic:claude-sonnet-5-5
    pip install langchain-openai      and   export OPENAI_API_KEY=...      and   export MODEL=openai:gpt-5-mini
    (Azure OpenAI: langchain-openai + AzureChatOpenAI; Amazon Bedrock: langchain-aws + ChatBedrockConverse)
Run:  python langchain_agent.py
"""
import os

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool


@tool
def get_password_policy() -> str:
    """Return Contoso's device password policy."""
    return "Minimum 12 characters, mixed character types, change every 90 days, no reuse of last 5."


@tool
def create_ticket(title: str, priority: str = "medium") -> str:
    """Create an IT support ticket and return its id."""
    return f"Ticket #1042 created: '{title}' (priority {priority})"


class ScriptedModel(GenericFakeChatModel):
    """Offline stand-in: replays scripted replies (first a tool call, then a final answer)."""

    def bind_tools(self, tools, **kwargs):
        return self


def build_model():
    if os.getenv("MODEL"):
        from langchain.chat_models import init_chat_model
        return init_chat_model(os.environ["MODEL"])        # e.g. "anthropic:claude-sonnet-5-5"
    return ScriptedModel(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "get_password_policy", "args": {}, "id": "call_1"}]),
        AIMessage(content="Your laptop password must be at least 12 characters with mixed character "
                          "types, and you must change it every 90 days (IT Security Policy)."),
    ]))


agent = create_agent(
    model=build_model(),
    tools=[get_password_policy, create_ticket],
    system_prompt="You are Contoso's IT helpdesk agent. Use tools for facts; cite the policy.",
)

if __name__ == "__main__":
    result = agent.invoke({"messages": [{"role": "user", "content": "How long must my laptop password be?"}]})
    for msg in result["messages"]:
        kind = type(msg).__name__
        text = msg.content or (f"tool_calls={[c['name'] for c in msg.tool_calls]}" if getattr(msg, "tool_calls", None) else "")
        print(f"{kind:>12}: {text}")
