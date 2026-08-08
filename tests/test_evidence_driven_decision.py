from services.decision_service import DecisionService
from services.evidence_service import EvidenceService


def test_evidence_service_builds_auditable_market_signals():
    evidence = EvidenceService().build(
        {
            "name": "GOLD",
            "trend": "BULLISH",
            "rsi": 28,
            "daily_change": 1.8,
            "volatility": 18,
        },
        sentiment={"positive": 8, "negative": 2},
        calendar_events=[{"name": "CPI"}],
        fact_validation={"confidence_score": 70},
    )

    assert len(evidence) >= 6
    assert all(item.evidence_id.startswith("ev-") for item in evidence)
    assert {item.kind for item in evidence} >= {
        "technical", "momentum", "risk", "sentiment", "macro", "validation"
    }


def test_decision_contains_evidence_without_changing_legacy_score():
    market = {
        "name": "GOLD",
        "price": 4000,
        "trend": "BULLISH",
        "rsi": 28,
        "daily_change": 1.8,
        "volatility": 18,
        "signal": "BUY",
    }
    evidence = EvidenceService().build(market, {"positive": 8, "negative": 2})

    result = DecisionService().analyze(
        market,
        sentiment={"positive": 8, "negative": 2},
        evidence=evidence,
    )

    assert result["score"] == 90
    assert result["bias"] == "BULLISH"
    assert result["evidence"]["count"] == len(evidence)
    assert result["evidence"]["items"]
