import json
from backend.structure import Email

#pushes extracted and processed data into processed inbox json 

def pushIt(emails : list):
    data = list()
    file = "sources/processed_inbox.json"
    for email in emails:
        data.append({
        "id": email.id,
        "message_id": email.message_id,
        "sender": email.sender,
        "sender_name": email.sender_name,
        "recipients": email.recipients,
        "subject": email.subject,
        "body": email.body,
        "timestamp": email.timestamp,
        "category": email.category,
        "priority": email.priority,
        "is_spam": email.is_spam,
        "action_items": email.action_items,
        "summary": email.summary,
        "has_attachment": email.has_attachment,
        "attachment_names": email.attachment_names
        })
    
    with open(file, 'w') as file:
        json.dump(data,file, indent=4) # indent for pretty-printing
