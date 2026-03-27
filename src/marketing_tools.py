import json
import os

def plan_campaign(product, features):
    try:
        from ollama import chat
        feature_names = [f["name"] if isinstance(f, dict) else f for f in features]
        res = chat(model='mistral', messages=[{
            'role': 'user',
            'content': (
                f"Plan a marketing campaign for {product} with features: {feature_names}. "
                "Respond ONLY with a JSON object with these keys: "
                "'product' (string), 'tagline' (string), 'channel' (string), "
                "'budget' (integer USD), 'expected_leads' (integer), 'timeline_weeks' (integer). "
                "No explanation, just the JSON object."
            )
        }])
        text = res.message.content.strip()
        text = text[text.index("{"):text.rindex("}") + 1]
        campaign = json.loads(text)
        campaign["product"] = campaign.get("product", product)
        campaign["features"] = feature_names
    except Exception:
        feature_names = [f["name"] if isinstance(f, dict) else f for f in features]
        campaign = {
            "product": product,
            "features": feature_names,
            "tagline": f"Unlock the power of {product}",
            "channel": "Email + Social Media",
            "budget": 8000,
            "expected_leads": 150,
            "timeline_weeks": 6
        }
    return campaign

def save_campaign(campaign):
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists("data/campaigns.json"):
        with open("data/campaigns.json", "r") as f:
            existing = json.load(f)
    existing.append(campaign)
    with open("data/campaigns.json", "w") as f:
        json.dump(existing, f, indent=2)
