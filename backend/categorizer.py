from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from backend.extractor import extractInbox, extractPrompts, pushInbox
from backend.structure import Email

load_dotenv()

def categorizer():
    inbox = extractInbox.extract()
    User_prompts = extractPrompts.extract()
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2)
    
    categorized_emails = list()
    
    for email in inbox:
        str_llm_json = llm.with_structured_output(Email, method="json_mode")
        
        prompt = f"""
                You are an Email Categorization Agent. Read the following {email["body"]} and classify it into exactly one of these categories:

    1. Important – time-sensitive or requires immediate attention.
    2. To-Do – contains a direct request, task, assignment, or instruction.
    3. Meeting Request – contains scheduling, invitations, or coordination messages.
    4. Project Update – contains progress updates, announcements, or work summaries.
    5. Newsletter – promotional, informational, or automated updates.
    6. Spam – irrelevant, overly promotional, or suspicious content.
    7. Personal – casual, friendly, non-work communication.
    
    Special Note:- This->
    {User_prompts["categorization_prompt"]}, 
    is given by the master user ,if there is are different commands for categorization use this instead for categorization.
    If there are any special or unique instruction given in this prompt. Give this the main priority. 
    If the email is catgorized as spam do not give it a priority
    Also,
    You are an Action Item Extraction Agent too. Extract all tasks the user must complete from the email.

A task must include:
- What needs to be done
- Optional deadline or timeline if mentioned

Respond with a bullet list of tasks. If no task exists, return: "No action items."


    Special Note:- This->
    {User_prompts["action_item_prompt"]}, 
    is given by the master user ,if there is are different way of giving the action-item by the user use this instead for action-item extraction.
    If there are any special or unique instruction given in this prompt. Give this the main priority. 
    If the email is catgorized as spam do not generate action item for it.
    
    And Lastly,
    
    Draft a formal and concise reply to the following email.
    Based on {User_prompts["auto_reply_prompt"]}
    If the email is catgorized as spam do not generate auto reply for it.
    If the sender email contain noreply then also do not generate auto reply for those too.
Structure:
1. Polite greeting
2. Acknowledgement of the received email
3. Clear response or confirmation
4. Any clarifying questions (if needed)
5. Polite closing

Do not invent facts. Do not include placeholders. Keep the tone professional.

    
    
"""
        categorized_emails.append(str_llm_json.invoke(prompt))
    
    return pushInbox.pushIt(categorized_emails)