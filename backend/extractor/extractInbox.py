
import json

def extract():
    InboxFile = "sources/inbox.json"
    with open(InboxFile,"r") as f:
        raw = json.load(f)
    emails = raw["emails"]
    return emails

# extract()