from langchain_core.tools import Tool,tool
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph,END,START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import Annotated,add_messages,TypedDict
import os 
from tools import send_email_tool
from dotenv import load_dotenv  

import sys
email_id = sys.argv[1]
content = sys.argv[2]

load_dotenv()

llm = ChatOpenAI(
    model="llama3.1:8b",
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
    temperature=0.0
)
class State(TypedDict):
    history : Annotated[list,add_messages]
    user_input : str
    subject : str
    content : str
    to_email : str
    
graph_builder = StateGraph(State)

def analyser_agent(state : State):
    messages =[SystemMessage(content= """
    This is used as an 
    analyser agent and its 
    work is to analyse the 
    user's input and classify 
    it.
    """),
    HumanMessage(content=f"can you analyse the email given by my client and classify it the mail is {state['user_input']}")
    ]
    result = llm.invoke(messages)
    return {
        "history" : [result],
    }
def reply_agent_subject(state : State):
    """
    This the the agent which helps 
    in analysing the data given by 
    analyser agent and it writes a 
    subject to the mail based on the analysis
    """
    messages = [
        SystemMessage(content="""
           Analyze the email content provided by the user and generate a concise, relevant reply email subject. The subject must be:
            Directly based on the analysis of the user’s message
            Maximum 8 words
            Clear, structured, and professional
            Do not include “Re:” or any extra text
            Only provide the subject line, nothing else"""),
            HumanMessage(content=f"""
            can you write a reply subject alone for mail and users message is {content}""")
    ]
    result = llm.invoke(messages)
    print(result.content)
    return {
        "history": [result],
        "subject" : result.content
    }
def reply_agent_emaiid(state : State):
    """
    This the the agent which helps 
    extrating email from user input
    """
    messages = [
        SystemMessage(content="""
            Your work is to analyse the data given by user and extract email id from the input
            only give email id as output no explanation and no extra any addings
            There is a possiblitiy of two email so i need only sender email so analyse carefully
             """),
            HumanMessage(content=f"""
            can you extract me email id and user input is : {email_id}""")
    ]
    result = llm.invoke(messages)
    print(result.content)
    return {
        "history": [result],
        "to_email" : result.content.strip()
    }
def reply_agent_content(state : State):
    """
    This the the agent which helps 
    in analysing the data given by 
    analyser agent and it writes a 
    reply letter based on the analysis
    """
    messages = [
        SystemMessage(content=f"""
            Analyze the email content provided by the user and generate a reply email content that is:
            Directly based on the user’s message
            Neat, structured, and reads like a natural human conversation
            Do not include any subject line or extra text
            Extract the recipient’s name from {email_id} and address them directly in the reply
                Always sign off as Ritik M
                Only provide the content, nothing else"""),
            HumanMessage(content=f"""
            can you write a reply mail based on analysis : {state['history'][-1].content} and
            users message is {content}""")
    ]
    result = llm.invoke(messages)
    print(result.content)
    return {
        "history": [result],
        "content" : result.content
    }

def send_email_agent(state : State):
    """
    This the the agent which helps 
    in sending mails to people with
    subject and content
    """
    tool_input = {
    "subject": state["subject"],
    "content": state["content"],
    "to_email": state["to_email"]
}
    send_email_tool.run(
        tool_input=tool_input   
    )
    return state
graph_builder.add_node("send mail" , send_email_agent)
graph_builder.add_node("content agent" , reply_agent_content)
graph_builder.add_node("subject agent" , reply_agent_subject)
graph_builder.add_node("emailid agent" , reply_agent_emaiid)
graph_builder.add_node("analyser" , analyser_agent)



graph_builder.add_edge(START , "analyser")
graph_builder.add_edge("analyser" , "subject agent")
graph_builder.add_edge("subject agent","content agent")
graph_builder.add_edge("content agent", "emailid agent")
graph_builder.add_edge("emailid agent", "send mail")
graph_builder.add_edge("send mail" , END)


graph = graph_builder.compile()
state = {"history" : [] , "user_input" : "","content" : "" , "subject" : "" ,"to_email" : ""}
state = graph.invoke(state)
print(state["subject"],state["content"],state["to_email"])
   
    