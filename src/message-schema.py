import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict

@dataclass
class Message:
    id: str
    timestamp: str
    sender: str
    recipient: str
    task_type: str
    context: Dict
    payload: Dict
    status: str
    error: str = ""
    
    @staticmethod
    def create(sender: str, recipient: str, task_type: str, context=None, payload=None):
        return Message(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat()+"Z",
            sender=sender,
            recipient=recipient,
            task_type=task_type,
            context=context or {},
            payload=payload or {},
            status="pending"
        )
    
    def to_dict(self):
        return asdict(self)
