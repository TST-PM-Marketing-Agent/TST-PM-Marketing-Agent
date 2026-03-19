import logging
from message_bus import get_messages_for, send_message
from message_schema import Message
from marketing_tools import plan_campaign, save_campaign

class MarketingAgent:
    def __init__(self, name="Marketing"):
        self.name = name
        logging.basicConfig(filename="logs/app.log", level=logging.INFO)
    
    def run(self):
        msgs = get_messages_for(self.name)
        for m in msgs:
            if m['task_type'] == "LAUNCH_CAMPAIGN":
                self.handle_launch_campaign(m)
            else:
                logging.warning(f"MarketingAgent: Unhandled {m['task_type']}")

    def handle_launch_campaign(self, msg):
        logging.info(f"MarketingAgent received campaign request: {msg['id']}")
        payload = msg['payload']
        product = payload.get("product_name", "Product")
        features = payload.get("features", [])
        campaign = plan_campaign(product, features)  # LLM call or stub
        logging.info(f"MarketingAgent plan: {campaign}")
        if campaign.get("budget", 0) > 10000:
            logging.info("Budget > $10k, escalating to CEO")
            send_message(Message.create(
                sender=self.name,
                recipient="CEO",
                task_type="BUDGET_APPROVAL",
                context={},
                payload=campaign
            ))
        else:
            save_campaign(campaign)  # writes data/campaigns.json
            logging.info("MarketingAgent: campaign saved")
