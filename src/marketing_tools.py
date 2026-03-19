import json

def plan_campaign(product, features):
    # call llm to plan campaign given product + features
    try:
        from ollama import chat
        res = chat(model='mistral', messages=[{'role': 'user', 'content':
            f"Plan a marketing campaign for {product} with features {features}"}])
        text = res.message.content
        # parse text into campaign dict
        campaign = {}  # parse text
    except Exception:
        campaign = {"product": product, "features": features,
                    "channel": "Email+Social", "budget": 8000, "expected_leads": 150}
    return campaign

def save_campaign(campaign):
    with open("data/campaigns.json", "w") as f:
        json.dump(campaign, f, indent=2)
