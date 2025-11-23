import json
#extracts user defined prompts from json files
def extract():
    PromptsFile = "sources/prompts.json"
    with open(PromptsFile,"r") as f:
        raw = json.load(f)
    return raw
