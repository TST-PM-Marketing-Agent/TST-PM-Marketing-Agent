import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from message_schema import Message


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, db_path: Optional[str] = None) -> None:
        configured = db_path or os.getenv("APP_DB_PATH", "data/agent_store.db")
        self.db_path = configured
        self.backlog_path = os.getenv("BACKLOG_PATH", "data/backlog.json")
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    goal TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS project_events (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message_id TEXT,
                    details_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    context_json TEXT NOT NULL DEFAULT '{}',
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    status TEXT NOT NULL,
                    error TEXT NOT NULL DEFAULT '',
                    project_id TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS backlog_entries (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    bucket TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    impact TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    campaign_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_project_id
                ON messages(project_id)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_events_project_id
                ON project_events(project_id)
                """
            )
            conn.commit()

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
        resolved_project_id = project_id or str(uuid.uuid4())
        resolved_description = description or metadata.get("description", "")

        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM projects WHERE id = ?",
                (resolved_project_id,),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE projects
                    SET name = ?, goal = ?, description = ?, status = ?, metadata_json = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        name,
                        goal,
                        resolved_description,
                        status,
                        json.dumps(metadata),
                        now,
                        resolved_project_id,
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO projects(id, name, goal, description, status, metadata_json, created_at, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        resolved_project_id,
                        name,
                        goal,
                        resolved_description,
                        status,
                        json.dumps(metadata),
                        now,
                        now,
                    ),
                )
            conn.commit()
        return self.get_project(resolved_project_id) or {}

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "goal": row["goal"],
                "description": row["description"],
                "status": row["status"],
                "payload": json.loads(row["metadata_json"] or "{}"),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    def find_active_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM projects
                WHERE name = ? AND status = 'active'
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (name,),
            ).fetchone()
            if not row:
                return None
            return self.get_project(row["id"])

    def add_project_event(
        self,
        *,
        source: str,
        event_type: str,
        project_id: Optional[str] = None,
        message_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO project_events(id, project_id, source, event_type, message_id, details_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    source,
                    event_type,
                    message_id,
                    json.dumps(details or {}),
                    _utc_now(),
                ),
            )
            if project_id:
                conn.execute(
                    "UPDATE projects SET updated_at = ? WHERE id = ?",
                    (_utc_now(), project_id),
                )
            conn.commit()

    def save_message(self, msg: Dict[str, Any]) -> None:
        Message.validate_envelope(msg)
        context = msg.get("context", {}) or {}
        project_id = context.get("project_id")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO messages(
                    id, timestamp, sender, recipient, task_type, context_json, payload_json, status, error, project_id
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    msg.get("id"),
                    msg.get("timestamp", _utc_now()),
                    msg.get("sender", ""),
                    msg.get("recipient", ""),
                    msg.get("task_type", ""),
                    json.dumps(context),
                    json.dumps(msg.get("payload", {}) or {}),
                    msg.get("status", "pending"),
                    msg.get("error", ""),
                    project_id,
                ),
            )
            if project_id:
                conn.execute(
                    "UPDATE projects SET updated_at = ? WHERE id = ?",
                    (_utc_now(), project_id),
                )
            conn.commit()

    def save_backlog(self, project_id: Optional[str], prioritized: Dict[str, List[Dict[str, Any]]]) -> None:
        # Always write the JSON artifact to preserve existing file-based outputs;
        # when project_id is missing, DB normalization is intentionally skipped.
        backlog_dir = os.path.dirname(self.backlog_path)
        if backlog_dir:
            os.makedirs(backlog_dir, exist_ok=True)
        with open(self.backlog_path, "w") as f:
            json.dump(prioritized, f, indent=2)
        if not project_id:
            return
        with self._connect() as conn:
            conn.execute("DELETE FROM backlog_entries WHERE project_id = ?", (project_id,))
            created_at = _utc_now()
            for bucket, items in prioritized.items():
                for feature in items:
                    conn.execute(
                        """
                        INSERT INTO backlog_entries(id, project_id, bucket, feature_name, impact, created_at)
                        VALUES(?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(uuid.uuid4()),
                            project_id,
                            bucket,
                            str(feature.get("name", "")),
                            str(feature.get("impact", "")),
                            created_at,
                        ),
                    )
            conn.execute(
                "UPDATE projects SET updated_at = ? WHERE id = ?",
                (_utc_now(), project_id),
            )
            conn.commit()

    def save_campaign(self, campaign: Dict[str, Any]) -> None:
        project_id = campaign.get("project_id")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO campaigns(id, project_id, campaign_json, created_at)
                VALUES(?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    json.dumps(campaign),
                    _utc_now(),
                ),
            )
            if project_id:
                conn.execute(
                    "UPDATE projects SET updated_at = ? WHERE id = ?",
                    (_utc_now(), project_id),
                )
            conn.commit()


storage = Storage()
