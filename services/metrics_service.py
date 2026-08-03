"""Persistent observability metrics for pipeline executions."""

import json
from datetime import datetime
from typing import Any

from models.domain import AgentStatus, ExecutionMetric
from services.database_service import DatabaseService
from services.logger import get_logger


logger = get_logger(__name__)


class MetricsService:
    """Record and query structured metrics without affecting workflow success."""

    def __init__(self, database_service: DatabaseService | None = None) -> None:
        self.db = database_service or DatabaseService()

    def record(self, metric: ExecutionMetric, metadata: dict[str, Any] | None = None) -> None:
        """Persist a metric for one agent execution."""
        self.db.connection.execute(
            """
            INSERT INTO execution_metrics (
                run_id, agent, status, started_at, duration_ms,
                item_count, error_count, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metric.run_id,
                metric.agent,
                metric.status.value,
                metric.started_at.isoformat(),
                metric.duration_ms,
                metric.item_count,
                metric.error_count,
                json.dumps(metadata or {}, sort_keys=True, default=str),
            ),
        )
        self.db.connection.commit()

    def for_run(self, run_id: str) -> list[dict[str, Any]]:
        """Return metrics ordered by insertion for one workflow run."""
        rows = self.db.connection.execute(
            """
            SELECT agent, status, duration_ms, item_count, error_count, metadata
            FROM execution_metrics
            WHERE run_id = ?
            ORDER BY id
            """,
            (run_id,),
        ).fetchall()
        return [
            {
                "agent": row[0],
                "status": row[1],
                "duration_ms": row[2],
                "item_count": row[3],
                "error_count": row[4],
                "metadata": json.loads(row[5]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self.db.close()
