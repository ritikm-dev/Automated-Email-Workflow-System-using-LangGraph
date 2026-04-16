from langchain.messages import HumanMessage,AIMessage,SystemMessage
import os 
from tools import send_email_tool
from llm import llm,State
import sys
email_id = sys.argv[1]
content = sys.argv[2]


def manager_agent(state : State):
    """
    This is agent is manager agent which will decide wheather 
    email reply needs human opinion or not needed
    """
    messages = [
    SystemMessage(content="""
Decide whether this email requires a human reply.

Return True immediately if:

The email contains or refers to:
meeting
schedule
availability
calendar
invite
join
attend
confirm
any date or time reference (e.g., tomorrow, Monday, 10 AM)

Return True if:

The response is needed to keep something moving forward within a timeframe

Return False only if:

The email is completely non-time-dependent
It is casual/social (e.g., birthday wishes, greetings, congratulations)
No action or coordination is required

Important:

Scheduling or meeting-related emails must ALWAYS return True
Do NOT treat them as optional
Do NOT rely on tone; rely on intent and keywords

Output ONLY:
True or False
"""),
    HumanMessage(content=f"{state['user_input']}")
]
    result = llm.invoke(messages)
    return {
        "history" : [result],
        "human_needed" : result.content
    }


def human_opinion_analyser_agent(state : State):
    """
    This will craete content for email 
    and it will ensure that it is related to
    human opinion where human opinion is needed.
    """
    s = input("Enter Opinion: ")
    state.update({
            "human_opinion" : s
                    })
    messages = [
    SystemMessage(content="""
Write a reply email.
INPUT:
Human Opinion: <ritik_actual_reply_here>
Sender Email: <email_id_here>
Original Message: <message_here>
STRICT RULES:
Only write the email body (NO subject line)
Do NOT include "Subject:" anywhere
Extract the recipient’s name ONLY from the Sender Email
(Example: shadhanan.project@gmail.com
 → Shadhanan)
Use that extracted name in the greeting
Ignore any names mentioned in the email content
Do NOT include the email ID in the response
Replace placeholders like [Sender Name] with: Ritik M
The Human Opinion is Ritik’s actual reply → use it as the source of truth
Rewrite the Human Opinion into a natural, clear, and slightly detailed email
Do NOT change the meaning of Human Opinion
Do NOT add new facts that are not present in Human Opinion
Always write from Ritik’s perspective (use “I”)
Do NOT assume anything about the recipient
Do NOT use comparison words like: also, too, same here, even I
unless explicitly mentioned in the Original Message
If Human Opinion is missing or unclear, give a safe, neutral, realistic reply without inventing details
Keep the tone natural and human-like
Avoid one-line replies; write at least 3–5 meaningful sentences
The response should feel complete and thoughtful
Format:
Hi <Extracted Name>,
<Clear, natural rewrite of Human Opinion without adding assumptions or comparisons>
Best regards,
Ritik M
"""),
        HumanMessage(content=f"{state['human_opinion']} and recipitent emailid : {email_id} and email content : {state['user_input']}")
]
    print("Human opinion original: ",state["human_opinion"])
   
    result = llm.invoke(messages)
    return {
            "history" : [result],
            "content" : result.content
        }


def no_human_opinion_agent(state : State):
    messages = [
    SystemMessage(content="""
Write a reply email.
STRICT RULES:
Only write the email body (NO subject line)
Do NOT include "Subject:" anywhere
Use the Recipient Name etracting from the Recipent email in the greeting
Do NOT change or infer the name
Do NOT use generic greetings like "Hi there"
Do NOT include the email ID
Replace placeholders like [Sender Name] with: Ritik M
Do NOT ask questions; respond confidently
Keep the tone natural and human-like
Write at least 3–6 meaningful sentences
Format:
Hi <Recipient Name>,
<Write a clear, natural reply>
Best regards,
Ritik M
"""),
             HumanMessage(content=f"Now You are ritik write an email for the content : {state["user_input"]} and Reciptent email is {email_id}" )
            ]
    result = llm.invoke(messages)
    return {
        "history" : [result],
        "content" : result.content
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
    print("human opinion subject",state["human_opinion"])
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
    print("human opinion emailid",state["human_opinion"])
    result = llm.invoke(messages)
    print(result.content)
    return {
        "history": [result],
        "to_email" : result.content.strip()
    }
# def reply_agent_content(state : State):
#     """
#     This the the agent which helps 
#     in analysing the data given by 
#     analyser agent and it writes a 
#     reply letter based on the analysis
#     """
#     messages = [
#         SystemMessage(content=f"""
#             Analyze the email content provided by the user and generate a reply email content that is:
#             Directly based on the user’s message
#             Neat, structured, and reads like a natural human conversation
#             Do not include any subject line or extra text
#             Extract the recipient’s name from {email_id} and address them directly in the reply
#                 Always sign off as Ritik M
#                 Only provide the content, nothing else"""),
#             HumanMessage(content=f"""
#             can you write a reply mail based on analysis : {state['history'][-1].content} and
#             users message is {content}""")
#     ]
#     result = llm.invoke(messages)
#     print(result.content)
#     return {
#         "history": [result],
#         "content" : result.content
#     }

def send_email_agent(state : State):
    """
    This the the agent which helps 
    in sending mails to people with
    subject and content
    """
    print("sending email")
    tool_input = {
    "subject": state["subject"],
    "content": state["content"],
    "to_email": state["to_email"],
}
    send_email_tool.run(
        tool_input=tool_input   
    )
    return state