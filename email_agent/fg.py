from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, Annotated
from pydantic import BaseModel

class State(BaseModel):
    messages: Annotated[list, add_messages]

builder = StateGraph(State)

def node_a(state: State):
    return State(messages=[{"role": "assistant", "content": "Hello"}])

def node_b(state: State):
    return State(messages=[{"role": "assistant", "content": "How are you?"}])

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
res = graph.invoke(State)
print(res)