import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class Message:
    id: str
    timestamp: str
    sender: str
    recipient: str
    task_type: str
    context: Dict[str, Any]
    payload: Dict[str, Any]
    status: str
    error: str = ""

    REQUIRED_FIELDS = (
        "id",
        "timestamp",
        "sender",
        "recipient",
        "task_type",
        "context",
        "payload",
        "status",
        "error",
    )
    VALID_STATUSES = {"pending", "in_progress", "done", "error"}

    @staticmethod
    def create(sender: str, recipient: str, task_type: str, context=None, payload=None):
        return Message(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=sender,
            recipient=recipient,
            task_type=task_type,
            context=context or {},
            payload=payload or {},
            status="pending",
        )

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def validate_envelope(message: Dict[str, Any]) -> None:
        missing = [k for k in Message.REQUIRED_FIELDS if k not in message]
        if missing:
            raise ValueError(f"Missing required envelope fields: {missing}")
        if not isinstance(message["context"], dict):
            raise ValueError("Envelope field 'context' must be an object.")
        if not isinstance(message["payload"], dict):
            raise ValueError("Envelope field 'payload' must be an object.")
        if message["status"] not in Message.VALID_STATUSES:
            raise ValueError(
                "Envelope field 'status' must be one of: pending, in_progress, done, error."
            )
