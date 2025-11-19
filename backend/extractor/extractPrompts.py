import json

def extract():
    PromptsFile = "sources/prompts.json"
    with open(PromptsFile,"r") as f:
        raw = json.load(f)
    return raw
