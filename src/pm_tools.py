import json
from message_schema import Message

def generate_features_llm(goal):
  # call mistral to gen a list of feature dicts
    try:
        from ollama import chat
        res = chat(model='mistral', messages=[{'role': 'user', 'content': f"List product features to achieve: {goal}"}])
        text = res.message.content
        # need to parse text into features (ie [name, impact])
        # currently assuming model returns json or list
        features = []  # parse text
    except Exception:
        features = [{"name": "Core feature", "impact": "high"}, {"name": "Extra feature", "impact": "low"}]
    return features

def moscow_prioritize(features):
    must = [f for f in features if f.get("impact") == "high"]
    should = [f for f in features if f.get("impact") != "high"]
    return {"must": must, "should": should, "could": [], "wont": []}

def save_backlog(data):
    with open("data/backlog.json", "w") as f:
        json.dump(data, f, indent=2)
