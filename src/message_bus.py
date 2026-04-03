import json
import os
from collections import deque
from storage import storage
from message_schema import Message

_message_queue = deque()
_MESSAGE_LOG = "data/messages.json"

def send_message(msg):
    if hasattr(msg, 'to_dict'):
        msg = msg.to_dict()
    Message.validate_envelope(msg)
    _message_queue.append(msg)
    _persist_message(msg)

def get_messages_for(agent_name):
    results = [m for m in list(_message_queue)
               if m['recipient'] in (agent_name, "broadcast")]
    for m in results:
        try:
            _message_queue.remove(m)
        except ValueError:
            pass
    return results

def _persist_message(msg):
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists(_MESSAGE_LOG):
        with open(_MESSAGE_LOG, "r") as f:
            existing = json.load(f)
    existing.append(msg)
    with open(_MESSAGE_LOG, "w") as f:
        json.dump(existing, f, indent=2)
    storage.save_message(msg)
