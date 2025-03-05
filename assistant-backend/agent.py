from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode
import datetime
from tools import get_next_available_meeting, reserve_meeting
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import Dict, List, Any

CONVERSATION = []

llm = ChatOpenAI(model="gpt-4o-mini")


def receive_message(message: str) -> List:
    CONVERSATION.append(HumanMessage(content=message, type="human"))
    state = {
        "messages": CONVERSATION,
    }
    new_state = caller_app.invoke(state)
    CONVERSATION.extend(new_state["messages"][len(CONVERSATION) :])
    return CONVERSATION


def agent(state: MessagesState) -> Dict[str, Any]:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    current_prague_time = current_time + datetime.timedelta(hours=1)
    state["current_time"] = current_time.strftime("%Y-%m-%d %H:%M")
    state["current_prague_time"] = current_prague_time.strftime("%Y-%m-%d %H:%M")
    response = model.invoke(state)
    return {"messages": [response]}


def should_continue(state: MessagesState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


# Define the system prompt
prompt = """You are a personal assistant for helping the user to book, edit or cancel appointments, you should check the available appointments before booking anything. Be polite and helpful. Please convert all times to Prague timezone. User will always communicate in Prague timezone.

Current UTC time: {current_time}
Current Prague time: {current_prague_time}
"""

# Set up tools
tools = [get_next_available_meeting, reserve_meeting]
tool_node = ToolNode(tools)

# Create the prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        ("placeholder", "{messages}"),
    ]
)

# Bind the prompt template to the LLM with tools
model = prompt_template | llm.bind_tools(tools)

# Create the workflow
workflow = StateGraph(MessagesState)

workflow.add_node("agent", agent)
workflow.add_node("action", tool_node)

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)
workflow.add_edge("action", "agent")

workflow.set_entry_point("agent")

# Compile the workflow
caller_app = workflow.compile()
