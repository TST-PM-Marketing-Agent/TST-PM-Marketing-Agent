import logging
from message_bus import get_messages_for, send_message
from message_schema import Message
from pm_tools import generate_features_llm, moscow_prioritize, save_backlog

class PMAgent:
    def __init__(self, name="PM"):
        self.name = name
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
      
        goal = msg['payload'].get("business_goal", "")
      
        features = generate_features_llm(goal) #llm call
      
        logging.info(f"PMAgent features: {features}")
        prioritized = moscow_prioritize(features)
      
        logging.info(f"PMAgent backlog: {prioritized}")
        save_backlog(prioritized)
        # send task to marketing
        feature_list = prioritized["must"] + prioritized["should"]
        send_message(Message.create(
            sender=self.name,
            recipient="Marketing",
            task_type="LAUNCH_CAMPAIGN",
            context={},
            payload={"product_name": msg['payload'].get("product_name", "Product"),
                     "features": feature_list}
        ))
        logging.info("PMAgent: LAUNCH_CAMPAIGN sent to Marketing")

    def handle_feature_request(self, msg):
        # feature ahandling logic
        pass
