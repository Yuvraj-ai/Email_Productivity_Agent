from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
from typing import TypedDict, Annotated, List, Dict, Any
import operator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages : Annotated[List[BaseMessage],operator.add]
    selected_email : Dict[str,Any] | None
    inbox : List[Dict[str,Any]]
    prompts : Dict[str, str]

# @tool(description="If No Specific email is selected agent can look for the possible answers here")
# def email_info() -> str:
#     return "It's sunny."
def extract_info():
    import json
    InboxFile = "sources/processed_inbox.json"
    with open(InboxFile,"r") as f:
        raw = json.load(f)
    emails = []
    for email in raw:
        emails.append({
        
        # "id": email.id,
        "message_id": email["message_id"],
        "sender": email["sender"],
        "sender_name": email["sender_name"],
        "recipients": email["recipients"],
        "subject": email["subject"],
        # "body": email.body,
        "timestamp": email["timestamp"],
        "category": email["category"],
        "priority": email["priority"],
        "is_spam": email['is_spam'],
        "action_items": email['action_items'],
        "summary": email['summary'],
        "has_attachment": email['has_attachment'],
        "attachment_names": email['attachment_names']
        
        })
    return emails


def call_model(state: AgentState):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        max_retries=2
    )
    
    messages = state['messages']
    selected_email = state.get("selected_email")
    prompts = state.get("prompts", {})
    inbox = state.get('inbox',[])
    
    system_text = """You are an intelligent Email Productivity Agent designed to help the user manage their inbox.
You can summarize emails, extract action items, draft replies, and answer general questions about the inbox.
"""
    if selected_email:
        system_text += f"\n\n--- CURRENTLY SELECTED EMAIL ---\n"
        system_text += f"From: {selected_email.get('sender')} ({selected_email.get('sender_name')})\n"
        system_text += f"Subject: {selected_email.get('subject')}\n"
        system_text += f"Date: {selected_email.get('timestamp')}\n"
        system_text += f"Category: {selected_email.get('category')}\n"
        system_text += f"Body:\n{selected_email.get('body')}\n"
        system_text += f"--------------------------------\n"
        system_text += "The user's query likely relates to this specific email. Use this context to answer."
    else:
        emails_info = extract_info()
        system_text += f"\n\n--- INBOX CONTEXT ---\n"
        system_text += f"No specific email is selected. You have access to {len(inbox)} emails in the inbox.\n"
        system_text += f"Feel free to use the {emails_info}, if the user asks about specific email, ask them to select one from the side bar."
        # system_text += "If the user asks about specific emails, ask them to select one from the sidebar or provide more details."

    system_text += "\n\n--- USER PREFERENCES & PROMPTS ---\n"
    if 'auto_reply_prompt' in prompts:
        system_text += f"DRAFTING REPLIES GUIDELINE: {prompts['auto_reply_prompt']}\n"
    if 'action_item_prompt' in prompts:
        system_text += f"EXTRACTING ACTIONS GUIDELINE: {prompts['action_item_prompt']}\n"
    if 'categorization_prompt' in prompts:
        system_text += f"CATEGORIZATION LOGIC: {prompts['categorization_prompt']}\n"

    system_text += "\nAnswer the user's request based on the context above. Be helpful, concise, and professional."

    conversation = [SystemMessage(content=system_text)] + messages
    
    response = llm.invoke(conversation)
    return {"messages": [response]}

def get_agent_response(user_query: str, chat_history: List[Dict], selected_email: Dict, inbox: List, prompts: Dict):
    """
    Entry point for the Streamlit app to call the agent.
    """
    lc_messages = []
    for msg in chat_history:
        if msg['role'] == 'user':
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg['role'] == "assistant":
            lc_messages.append(AIMessage(content=msg['content']))
    
    lc_messages.append(HumanMessage(content=user_query))
    
    workflow = StateGraph(AgentState)
    workflow.add_node("agent",call_model)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent",END)
    app = workflow.compile()
    
    inputs = {
        "messages": lc_messages,
        "selected_email": selected_email,
        "inbox": inbox,
        "prompts": prompts
    }
    
    result = app.invoke(inputs)

    return result['messages'][-1].content