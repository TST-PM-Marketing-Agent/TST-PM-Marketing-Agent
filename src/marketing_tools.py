import json
import os
from llm_provider import llm_json_object
from storage import storage

def plan_campaign(product, features):
    feature_names = [f["name"] if isinstance(f, dict) else f for f in features]
    prompt = (
        f"Plan a marketing campaign for {product} with features: {feature_names}. "
        "Respond ONLY with a JSON object with these keys: "
        "'product' (string), 'tagline' (string), 'channel' (string), "
        "'budget' (integer USD), 'expected_leads' (integer), 'timeline_weeks' (integer). "
        "No explanation, just the JSON object."
    )
    campaign = llm_json_object(prompt)
    if campaign:
        campaign["product"] = campaign.get("product", product)
        campaign["features"] = feature_names
    else:
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
    storage.save_campaign(campaign)
