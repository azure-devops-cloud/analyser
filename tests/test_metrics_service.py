from datetime import datetime, timezone

from models.domain import AgentStatus, ExecutionMetric
from services.database_service import DatabaseService
from services.metrics_service import MetricsService


def test_metrics_service_persists_agent_execution(tmp_path):
    database = DatabaseService(tmp_path / "marketmind.db")
    service = MetricsService(database)
    service.record(
        ExecutionMetric(
            run_id="run-1",
            agent="news_agent",
            status=AgentStatus.SUCCESS,
            started_at=datetime.now(timezone.utc),
            duration_ms=10.0,
            item_count=5,
        ),
        metadata={"feed_count": 2},
    )

    metrics = service.for_run("run-1")
    service.close()

    assert metrics[0]["agent"] == "news_agent"
    assert metrics[0]["metadata"] == {"feed_count": 2}
