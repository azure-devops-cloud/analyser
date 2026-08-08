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

    # This is the score produced by the pre-evidence DecisionService for
    # the same inputs. Adding evidence must not alter it.
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["evidence"]["count"] == len(evidence)
    assert result["evidence"]["items"]


def test_evidence_is_descriptive_and_cannot_change_score():
    market = {
        "name": "GOLD",
        "price": 4000,
        "trend": "BULLISH",
        "rsi": 28,
        "daily_change": 1.8,
        "volatility": 18,
        "signal": "BUY",
    }

    baseline = DecisionService().analyze(
        market,
        sentiment={"positive": 8, "negative": 2},
    )
    evidence = EvidenceService().build(
        market,
        sentiment={"positive": 8, "negative": 2},
        calendar_events=[{"name": "CPI"}],
        fact_validation={"confidence_score": 95},
    )
    with_evidence = DecisionService().analyze(
        market,
        sentiment={"positive": 8, "negative": 2},
        evidence=evidence,
    )

    assert baseline["score"] == 100
    assert with_evidence["score"] == baseline["score"]
    assert with_evidence["evidence"]["count"] == len(evidence)
