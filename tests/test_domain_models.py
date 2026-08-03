from datetime import datetime, timezone

from models.domain import AgentStatus, ExecutionMetric, MarketObservation


def test_typed_domain_models_capture_execution_contracts():
    observation = MarketObservation(
        name="BITCOIN",
        symbol="BTC-USD",
        price=100_000.0,
        captured_at=datetime.now(timezone.utc),
    )
    metric = ExecutionMetric(
        run_id="run-1",
        agent="market_agent",
        status=AgentStatus.SUCCESS,
        started_at=observation.captured_at,
        duration_ms=12.5,
        item_count=1,
    )

    assert observation.symbol == "BTC-USD"
    assert metric.status == "success"
