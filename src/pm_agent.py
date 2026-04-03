import logging
import os
from message_bus import get_messages_for, send_message
from message_schema import Message
from pm_tools import generate_features_llm, moscow_prioritize, save_backlog, create_project, add_request_to_project

class PMAgent:
    def __init__(self, name="PM"):
        self.name = name
        self._active_project = None
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(filename="logs/app.log", level=logging.INFO)

    def run(self):
        msgs = get_messages_for(self.name)
        for m in msgs:
            task = m['task_type']
            if task == "DEFINE_Q2_ROADMAP":
                self.handle_define_roadmap(m)
            elif task == "REQUEST_FEATURES":
                self.handle_feature_request(m)
            else:
                logging.warning(f"PMAgent: Unhandled task {task}")

    def handle_define_roadmap(self, msg):
        logging.info(f"PMAgent received roadmap request: {msg['id']}")
        payload = msg['payload']
        goal = payload.get("business_goal", "")
        product = payload.get("product_name", "Product")

        project = create_project(name=product, goal=goal, payload=payload)
        self._active_project = project
        logging.info(f"PMAgent created project: {project['id']}")

        features = generate_features_llm(goal)
        logging.info(f"PMAgent features: {features}")

        prioritized = moscow_prioritize(features)
        logging.info(f"PMAgent backlog: {prioritized}")

        save_backlog(prioritized)

        add_request_to_project(project["id"], {
            "type": "roadmap",
            "message_id": msg["id"],
            "features": features
        })

        feature_list = prioritized["must"] + prioritized["should"]
        send_message(Message.create(
            sender=self.name,
            recipient="Marketing",
            task_type="LAUNCH_CAMPAIGN",
            context={"project_id": project["id"]},
            payload={"product_name": product, "features": feature_list}
        ))
        logging.info("PMAgent: LAUNCH_CAMPAIGN sent to Marketing")

        send_message(Message.create(
            sender=self.name,
            recipient="Marketing",
            task_type="PM_REPORT",
            context={"project_id": project["id"]},
            payload={
                "project_name": product,
                "must_count": len(prioritized["must"]),
                "should_count": len(prioritized["should"]),
                "status": "roadmap_defined"
            }
        ))
        logging.info("PMAgent: PM_REPORT sent to Marketing")

    def handle_feature_request(self, msg):
        logging.info(f"PMAgent received feature request: {msg['id']}")
        payload = msg['payload']
        goal = payload.get("goal", "")
        requester = msg['sender']

        features = generate_features_llm(goal)
        prioritized = moscow_prioritize(features)

        project_id = None
        if self._active_project:
            project_id = self._active_project["id"]
            add_request_to_project(project_id, {
                "type": "feature_request",
                "requester": requester,
                "message_id": msg["id"],
                "features": features
            })

        send_message(Message.create(
            sender=self.name,
            recipient=requester,
            task_type="FEATURE_RESPONSE",
            context={"project_id": project_id},
            payload={"features": prioritized}
        ))
        logging.info(f"PMAgent: FEATURE_RESPONSE sent to {requester}")
