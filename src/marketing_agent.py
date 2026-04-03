import logging
import os
from message_bus import get_messages_for
from marketing_tools import plan_campaign, save_campaign
from storage import storage

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
            elif m['task_type'] == "PM_REPORT":
                self.handle_pm_report(m)
            else:
                logging.warning(f"MarketingAgent: Unhandled {m['task_type']}")

    def handle_pm_report(self, msg):
        logging.info(f"MarketingAgent received PM report: {msg['id']}")
        project_id = msg.get("context", {}).get("project_id")
        storage.add_project_event(
            source=self.name,
            event_type="pm_report_received",
            project_id=project_id,
            message_id=msg["id"],
            details=msg.get("payload", {}),
        )

    def handle_launch_campaign(self, msg):
        logging.info(f"MarketingAgent received campaign request: {msg['id']}")
        payload = msg['payload']
        product = payload.get("product_name", "Product")
        features = payload.get("features", [])
        project_id = msg.get("context", {}).get("project_id")

        campaign = plan_campaign(product, features)
        campaign["project_id"] = project_id
        logging.info(f"MarketingAgent plan: {campaign}")
        save_campaign(campaign)
        storage.add_project_event(
            source=self.name,
            event_type="campaign_saved",
            project_id=project_id,
            message_id=msg["id"],
            details={"product_name": product, "budget": campaign.get("budget")},
        )
        logging.info("MarketingAgent: campaign saved")
