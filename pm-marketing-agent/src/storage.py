import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
 
from message_schema import Message

try:
    from pymongo import MongoClient, DESCENDING
except ImportError:
    MongoClient = None
    DESCENDING = -1

class InMemoryCollectionMock:
    def __init__(self) -> None:
        self.docs: Dict[str, Dict[str, Any]] = {}

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        pass

    def find_one(self, filter: Dict[str, Any], sort: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        # filter is typically {"_id": resolved_id} or {"name": name, "status": "active"}
        for doc in self.docs.values():
            match = True
            for k, v in filter.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc.copy()
        return None

    def insert_one(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        self.docs[doc["_id"]] = doc.copy()
        return doc

    def update_one(self, filter: Dict[str, Any], update: Dict[str, Any]) -> bool:
        # update is typically {"$set": {...}}
        doc = self.find_one(filter)
        if doc:
            real_doc = self.docs[doc["_id"]]
            if "$set" in update:
                for k, v in update["$set"].items():
                    real_doc[k] = v
            return True
        return False

    def replace_one(self, filter: Dict[str, Any], replacement: Dict[str, Any], upsert: bool = False) -> None:
        doc = self.find_one(filter)
        if doc:
            self.docs[doc["_id"]] = replacement.copy()
            self.docs[doc["_id"]]["_id"] = doc["_id"]
        elif upsert:
            resolved_id = filter.get("_id") or replacement.get("_id") or str(uuid.uuid4())
            replacement["_id"] = resolved_id
            self.docs[resolved_id] = replacement.copy()

    def delete_many(self, filter: Dict[str, Any]) -> None:
        to_delete = []
        for doc in self.docs.values():
            match = True
            for k, v in filter.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                to_delete.append(doc["_id"])
        for _id in to_delete:
            self.docs.pop(_id, None)

    def insert_many(self, docs: List[Dict[str, Any]]) -> None:
        for doc in docs:
            self.insert_one(doc)


class InMemoryMongoMock:
    def __init__(self) -> None:
        self.collections: Dict[str, InMemoryCollectionMock] = {}

    def __getitem__(self, name: str) -> InMemoryCollectionMock:
        if name not in self.collections:
            self.collections[name] = InMemoryCollectionMock()
        return self.collections[name]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
 
 
class Storage:
    def __init__(self, mongo_uri: Optional[str] = None, db_name: Optional[str] = None) -> None:
        uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        name = db_name or os.getenv("MONGO_DB_NAME", "agent_store")
        self.backlog_path = os.getenv("BACKLOG_PATH", "data/backlog.json")
        
        self.use_mongo = False
        if MongoClient is not None:
            try:
                # serverSelectionTimeoutMS=1000 ensures it fails quickly if offline
                self.client = MongoClient(uri, serverSelectionTimeoutMS=1000)
                self.client.admin.command('ping')
                self.db = self.client[name]
                self._init_db()
                self.use_mongo = True
            except Exception:
                pass
        
        if not self.use_mongo:
            print("MongoDB not available or pymongo not installed. Using high-fidelity in-memory storage.")
            self.db = InMemoryMongoMock()  # type: ignore
 
    def _init_db(self) -> None:
        self.db["messages"].create_index("project_id")
        self.db["project_events"].create_index("project_id")
 
    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------
 
    def upsert_project(
        self,
        *,
        name: str,
        goal: str = "",
        payload: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        status: str = "active",
    ) -> Dict[str, Any]:
        metadata = payload or {}
        now = _utc_now()
        resolved_id = project_id or str(uuid.uuid4())
        resolved_description = description or metadata.get("description", "")
 
        existing = self.db["projects"].find_one({"_id": resolved_id})
        if existing:
            self.db["projects"].update_one(
                {"_id": resolved_id},
                {"$set": {
                    "name": name,
                    "goal": goal,
                    "description": resolved_description,
                    "status": status,
                    "metadata": metadata,
                    "updated_at": now,
                }},
            )
        else:
            self.db["projects"].insert_one({
                "_id": resolved_id,
                "name": name,
                "goal": goal,
                "description": resolved_description,
                "status": status,
                "metadata": metadata,
                "created_at": now,
                "updated_at": now,
            })
        return self.get_project(resolved_id) or {}
 
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db["projects"].find_one({"_id": project_id})
        if not doc:
            return None
        return {
            "id": doc["_id"],
            "name": doc["name"],
            "goal": doc.get("goal", ""),
            "description": doc.get("description", ""),
            "status": doc.get("status", "active"),
            "payload": doc.get("metadata", {}),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
        }
 
    def find_active_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        doc = self.db["projects"].find_one(
            {"name": name, "status": "active"},
            sort=[("updated_at", DESCENDING)],
        )
        if not doc:
            return None
        return self.get_project(doc["_id"])
 
    # ------------------------------------------------------------------
    # Project events
    # ------------------------------------------------------------------
 
    def add_project_event(
        self,
        *,
        source: str,
        event_type: str,
        project_id: Optional[str] = None,
        message_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = _utc_now()
        self.db["project_events"].insert_one({
            "_id": str(uuid.uuid4()),
            "project_id": project_id,
            "source": source,
            "event_type": event_type,
            "message_id": message_id,
            "details": details or {},
            "created_at": now,
        })
        if project_id:
            self.db["projects"].update_one(
                {"_id": project_id},
                {"$set": {"updated_at": now}},
            )
 
    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------
 
    def save_message(self, msg: Dict[str, Any]) -> None:
        Message.validate_envelope(msg)
        context = msg.get("context", {}) or {}
        project_id = context.get("project_id")
        now = _utc_now()
 
        self.db["messages"].replace_one(
            {"_id": msg.get("id")},
            {
                "_id": msg.get("id"),
                "timestamp": msg.get("timestamp", now),
                "sender": msg.get("sender", ""),
                "recipient": msg.get("recipient", ""),
                "task_type": msg.get("task_type", ""),
                "context": context,
                "payload": msg.get("payload", {}) or {},
                "status": msg.get("status", "pending"),
                "error": msg.get("error", ""),
                "project_id": project_id,
            },
            upsert=True,
        )
        if project_id:
            self.db["projects"].update_one(
                {"_id": project_id},
                {"$set": {"updated_at": now}},
            )
 
    # ------------------------------------------------------------------
    # Backlog
    # ------------------------------------------------------------------
 
    def save_backlog(
        self,
        project_id: Optional[str],
        prioritized: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        # Keep the JSON file artifact for backward compatibility
        backlog_dir = os.path.dirname(self.backlog_path)
        if backlog_dir:
            os.makedirs(backlog_dir, exist_ok=True)
        with open(self.backlog_path, "w") as f:
            json.dump(prioritized, f, indent=2)
 
        if not project_id:
            return
 
        self.db["backlog_entries"].delete_many({"project_id": project_id})
        created_at = _utc_now()
        docs = []
        for bucket, items in prioritized.items():
            for feature in items:
                docs.append({
                    "_id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "bucket": bucket,
                    "feature_name": str(feature.get("name", "")),
                    "impact": str(feature.get("impact", "")),
                    "created_at": created_at,
                })
        if docs:
            self.db["backlog_entries"].insert_many(docs)
 
        self.db["projects"].update_one(
            {"_id": project_id},
            {"$set": {"updated_at": _utc_now()}},
        )
 
    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------
 
    def save_campaign(self, campaign: Dict[str, Any]) -> None:
        project_id = campaign.get("project_id")
        now = _utc_now()
        self.db["campaigns"].insert_one({
            "_id": str(uuid.uuid4()),
            "project_id": project_id,
            "campaign": campaign,
            "created_at": now,
        })
        if project_id:
            self.db["projects"].update_one(
                {"_id": project_id},
                {"$set": {"updated_at": now}},
            )
 
 
storage = Storage()
