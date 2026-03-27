import logging
import os
from message_bus import get_messages_for, send_message
from message_schema import Message
from marketing_tools import plan_campaign, save_campaign

class MarketingAgent:
    def __init__(self, name="Marketing"):
        self.name = name
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(filename="logs/app.log", level=logging.INFO)

    def run(self):
        msgs = get_messages_for(self.name)
        for m in msgs:
            if m['task_type'] == "LAUNCH_CAMPAIGN":
                self.handle_launch_campaign(m)
            elif m['task_type'] == "BUDGET_APPROVED":
                self.handle_budget_approved(m)
            else:
                logging.warning(f"MarketingAgent: Unhandled {m['task_type']}")

    def handle_launch_campaign(self, msg):
        logging.info(f"MarketingAgent received campaign request: {msg['id']}")
        payload = msg['payload']
        product = payload.get("product_name", "Product")
        features = payload.get("features", [])
        project_id = msg.get("context", {}).get("project_id")

        campaign = plan_campaign(product, features)
        campaign["project_id"] = project_id
        logging.info(f"MarketingAgent plan: {campaign}")

        if campaign.get("budget", 0) > 10000:
            logging.info("Budget > $10k, escalating to CEO")
            send_message(Message.create(
                sender=self.name,
                recipient="CEO",
                task_type="BUDGET_APPROVAL",
                context={"project_id": project_id},
                payload=campaign
            ))
        else:
            save_campaign(campaign)
            logging.info("MarketingAgent: campaign saved")

    def handle_budget_approved(self, msg):
        logging.info(f"MarketingAgent: budget approved for message {msg['id']}")
        campaign = msg['payload']
        save_campaign(campaign)
        logging.info("MarketingAgent: approved campaign saved")
