import json
import uuid
import os
from datetime import datetime, timezone

def generate_features_llm(goal):
    try:
        from ollama import chat
        res = chat(model='mistral', messages=[{
            'role': 'user',
            'content': (
                f"List 6 product features to achieve this goal: {goal}. "
                "Respond ONLY with a JSON array. Each item must have 'name' (string) "
                "and 'impact' (one of: high, medium, low). "
                "Example: [{\"name\": \"Feature A\", \"impact\": \"high\"}]"
            )
        }])
        text = res.message.content.strip()
        text = text[text.index("["):text.rindex("]") + 1]
        features = json.loads(text)
    except Exception:
        features = [
            {"name": "AI-Powered Analytics Dashboard", "impact": "high"},
            {"name": "Multi-Tenant SSO Integration", "impact": "high"},
            {"name": "Automated Onboarding Flow", "impact": "high"},
            {"name": "Usage-Based Billing Module", "impact": "medium"},
            {"name": "In-App Help Center", "impact": "medium"},
            {"name": "Dark Mode UI", "impact": "low"},
        ]
    return features

def moscow_prioritize(features):
    must = [f for f in features if f.get("impact") == "high"]
    should = [f for f in features if f.get("impact") == "medium"]
    could = [f for f in features if f.get("impact") == "low"]
    wont = [f for f in features if f.get("impact") not in ("high", "medium", "low")]
    return {"must": must, "should": should, "could": could, "wont": wont}

def save_backlog(data):
    os.makedirs("data", exist_ok=True)
    with open("data/backlog.json", "w") as f:
        json.dump(data, f, indent=2)

def create_project(name, goal, payload):
    os.makedirs("data", exist_ok=True)
    projects = []
    if os.path.exists("data/projects.json"):
        with open("data/projects.json", "r") as f:
            projects = json.load(f)
    project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "goal": goal,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "requests": []
    }
    projects.append(project)
    with open("data/projects.json", "w") as f:
        json.dump(projects, f, indent=2)
    return project

def add_request_to_project(project_id, request):
    if not os.path.exists("data/projects.json"):
        return
    with open("data/projects.json", "r") as f:
        projects = json.load(f)
    for p in projects:
        if p["id"] == project_id:
            p["requests"].append(request)
            break
    with open("data/projects.json", "w") as f:
        json.dump(projects, f, indent=2)
