from main import build_report, build_report_payload
from models.agent_result import AgentResult


def _results():
    return [
        AgentResult(
            agent="summary_agent",
            status="success",
            data={
                "headline": "Executive view: Bullish posture | Lead: GOLD",
                "top_opportunity": "GOLD",
                "market_posture": "Bullish",
                "risk_watch": "Monitor confirmation",
                "action_recommendation": "Maintain selective exposure",
                "alerts": [],
            },
            count=1,
        ),
        AgentResult(
            agent="news_intelligence_agent",
            status="success",
            data=[
                {
                    "title": "Fed signals rate cut",
                    "impact": "HIGH",
                    "why_it_matters": "This may change rate expectations.",
                    "affected_assets": ["GOLD", "USD_INR"],
                    "evidence_id": "news-abc123",
                    "actions": ["Verify the primary source"],
                }
            ],
            count=1,
        ),
    ]


def test_report_contains_actionable_news_fields():
    report = build_report(_results(), 3)

    assert "Actionable News" in report
    assert "Fed signals rate cut" in report
    assert "Why: This may change rate expectations." in report
    assert "Affected: GOLD, USD_INR" in report
    assert "Evidence: news-abc123" in report
    assert "Next: Verify the primary source" in report


def test_report_payload_exposes_ranked_news():
    payload = build_report_payload(_results(), 3)

    assert payload["workflow_health"] == "healthy"
    assert payload["actionable_news"][0]["evidence_id"] == "news-abc123"
    assert payload["actionable_news"][0]["affected_assets"] == ["GOLD", "USD_INR"]
