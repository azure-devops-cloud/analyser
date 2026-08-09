"""Small durable episodic/semantic memory store using SQLite.

Memory is intentionally selective. Only compact workflow facts, outcomes, and
validated evidence references are persisted; raw secrets and untrusted prompts
are never stored by this component.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_key TEXT NOT NULL UNIQUE,
                    memory_type TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT
                )"""
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_agent_memory_type_updated "
                "ON agent_memory(memory_type, updated_at)"
            )

    def put(self, key: str, memory_type: str, value: Any, ttl_days: int | None = None) -> None:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ttl_days) if ttl_days else None
        payload = json.dumps(value, default=str, sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO agent_memory(memory_key,memory_type,value_json,created_at,updated_at,expires_at)
                   VALUES(?,?,?,?,?,?)
                   ON CONFLICT(memory_key) DO UPDATE SET
                     memory_type=excluded.memory_type,
                     value_json=excluded.value_json,
                     updated_at=excluded.updated_at,
                     expires_at=excluded.expires_at""",
                (key, memory_type, payload, now.isoformat(), now.isoformat(), expires.isoformat() if expires else None),
            )

    def get(self, key: str) -> Any | None:
        self.purge_expired()
        with self._connect() as conn:
            row = conn.execute("SELECT value_json FROM agent_memory WHERE memory_key=?", (key,)).fetchone()
        return json.loads(row["value_json"]) if row else None

    def search(self, memory_type: str, limit: int = 20) -> list[dict[str, Any]]:
        self.purge_expired()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT memory_key,value_json,updated_at FROM agent_memory "
                "WHERE memory_type=? ORDER BY updated_at DESC LIMIT ?",
                (memory_type, max(1, limit)),
            ).fetchall()
        return [
            {"key": row["memory_key"], "value": json.loads(row["value_json"]), "updated_at": row["updated_at"]}
            for row in rows
        ]

    def put_many(self, items: Iterable[tuple[str, str, Any]]) -> None:
        for key, memory_type, value in items:
            self.put(key, memory_type, value)

    def purge_expired(self) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM agent_memory WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,),
            )
            return cur.rowcount
