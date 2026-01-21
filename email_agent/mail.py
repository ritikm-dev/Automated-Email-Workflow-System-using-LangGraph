from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages,Annotated
from langchain_openai import ChatOpenAI
from typing import List
from langchain_core.messages import HumanMessage,AIMessage
from pydantic import BaseModel
import random
import os
from dotenv import load_dotenv
load_dotenv(override=True)
current_state = {"messages" : []}
model = ChatOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("GEMINI_BASE_URL"),
    model="gemini-2.5-flash-lite"
)


class State(BaseModel):
    messages : Annotated[list,add_messages]


graph_builder = StateGraph(State)


def read_mails(old_state : State):
    result = model.invoke(old_state.messages)
    new_state = State(messages=[AIMessage(content=result.content)])
    return new_state
graph_builder.add_node(read_mails,"read_mails")



def send_mails(old_state : State):
    new_state = State(messages=[])
    return new_state
graph_builder.add_node(send_mails,"send_mails")


graph_builder.add_edge(START,"read_mails")
graph_builder.add_edge("read_mails","send_mails")
graph_builder.add_edge("send_mails",END)

graph = graph_builder.compile()

while(1):
    s=input()
    current_state["messages"].append(HumanMessage(content=s))
    result = graph.invoke(current_state)
    current_state = result
    #print(result)
    #print(current_state)
