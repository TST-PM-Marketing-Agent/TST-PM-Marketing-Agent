import json
import logging
import os
from datetime import datetime, timezone

from message_bus import get_messages_for, send_message
from message_schema import Message


class CEOAgent:
    def __init__(self, name="CEO"):
        self.name = name
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(filename="logs/app.log", level=logging.INFO)

    def run(self):
        msgs = get_messages_for(self.name)
        for m in msgs:
            task = m["task_type"]
            if task == "START_BUSINESS_CYCLE":
                self.handle_start_cycle(m)
            elif task == "PM_REPORT":
                self.handle_report(m)
            elif task == "MARKETING_REPORT":
                self.handle_report(m)
            elif task == "BUDGET_APPROVAL":
                self.handle_budget_approval(m)
            else:
                logging.warning(f"CEOAgent: Unhandled task {task}")

    def handle_start_cycle(self, msg):
        logging.info(f"CEOAgent received start cycle request: {msg['id']}")
        payload = msg["payload"]
        context = msg.get("context", {})

        send_message(
            Message.create(
                sender=self.name,
                recipient="PM",
                task_type="DEFINE_Q2_ROADMAP",
                context=context,
                payload=payload,
            )
        )

        send_message(
            Message.create(
                sender=self.name,
                recipient="Marketing",
                task_type="PREPARE_CAMPAIGN_STRATEGY",
                context=context,
                payload=payload,
            )
        )
        logging.info("CEOAgent delegated tasks to PM and Marketing")

    def handle_report(self, msg):
        logging.info(f"CEOAgent received report: {msg['id']} from {msg['sender']}")
        os.makedirs("data", exist_ok=True)
        path = "data/ceo_reports.json"
        reports = []
        if os.path.exists(path):
            with open(path, "r") as f:
                reports = json.load(f)
        reports.append(
            {
                "received_at": datetime.now(timezone.utc).isoformat(),
                "message": msg,
            }
        )
        with open(path, "w") as f:
            json.dump(reports, f, indent=2)

    def handle_budget_approval(self, msg):
        logging.info(f"CEOAgent received budget approval request: {msg['id']}")
        campaign = msg["payload"]
        campaign["approved_by"] = self.name
        campaign["approved_at"] = datetime.now(timezone.utc).isoformat()
        send_message(
            Message.create(
                sender=self.name,
                recipient="Marketing",
                task_type="BUDGET_APPROVED",
                context=msg.get("context", {}),
                payload=campaign,
            )
        )
        logging.info("CEOAgent approved campaign budget and notified Marketing")
