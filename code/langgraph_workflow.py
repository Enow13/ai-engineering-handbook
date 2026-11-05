"""LangGraph 1.x workflow: state, nodes, conditional routing, checkpointing and human-in-the-loop.

An IT request is classified, routed, and password resets need human approval before running.
Runs WITHOUT an API key (the classifier is a simple rule; swap in an LLM call in real projects).
Run:  python langgraph_workflow.py
"""
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict, total=False):
    request: str
    category: str
    approved: bool
    result: str


def classify(state: State) -> dict:
    text = state["request"].lower()
    category = "password_reset" if "password" in text else "general"
    return {"category": category}                       # nodes return PARTIAL state updates


def route(state: State) -> Literal["approval", "answer"]:
    return "approval" if state["category"] == "password_reset" else "answer"


def approval(state: State) -> dict:
    # Pauses the graph and waits for a human. State is saved by the checkpointer.
    decision = interrupt({"question": f"Approve password reset for: '{state['request']}'?"})
    return {"approved": decision == "yes"}


def reset_password(state: State) -> dict:
    if not state.get("approved"):
        return {"result": "Password reset rejected by the approver."}
    return {"result": "Password reset link sent to the user's registered email."}


def answer(state: State) -> dict:
    return {"result": "Routed to the general IT queue."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("approval", approval)
builder.add_node("reset_password", reset_password)
builder.add_node("answer", answer)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)
builder.add_edge("approval", "reset_password")
builder.add_edge("reset_password", END)
builder.add_edge("answer", END)

graph = builder.compile(checkpointer=InMemorySaver())   # checkpointer = memory + pause/resume

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "ticket-42"}}   # one thread = one conversation/workflow

    first = graph.invoke({"request": "I forgot my password"}, config)
    print("Paused for approval:", first["__interrupt__"][0].value)

    final = graph.invoke(Command(resume="yes"), config)       # the human answers; graph resumes
    print("Category:", final["category"], "| Approved:", final["approved"])
    print("Result:", final["result"])

    other = graph.invoke({"request": "My monitor flickers"}, {"configurable": {"thread_id": "ticket-43"}})
    print("Other request:", other["result"])
