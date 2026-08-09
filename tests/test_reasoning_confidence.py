from services.reasoner_service import ReasonerService


def evidence(evidence_id, claim, strength=1.0, asset="GOLD"):
    return {
        "evidence_id": evidence_id,
        "asset": asset,
        "kind": "technical",
        "claim": claim,
        "value": 1,
        "strength": strength,
        "source": "test",
        "metadata": {},
    }


def test_strong_consistent_evidence_has_high_reasoning_confidence():
    result = ReasonerService().analyze(
        {"name": "GOLD", "bias": "BULLISH", "score": 90, "confidence": "HIGH"},
        [evidence("ev-1", "Trend is BULLISH"), evidence("ev-2", "Trend is BULLISH")],
    )
    assert result["reasoning_confidence"] == 100.0
    assert result["score"] == 90
    assert result["bias"] == "BULLISH"


def test_low_quality_evidence_reduces_reasoning_confidence_only():
    result = ReasonerService().analyze(
        {"name": "GOLD", "bias": "BULLISH", "score": 90, "confidence": "HIGH"},
        [evidence("ev-1", "Trend is BULLISH", strength=0.2)],
    )
    assert result["reasoning_confidence"] < 100.0
    assert result["score"] == 90
    assert result["bias"] == "BULLISH"
    assert result["confidence"] == "HIGH"


def test_contradiction_reduces_reasoning_confidence_without_changing_decision():
    result = ReasonerService().analyze(
        {"name": "GOLD", "bias": "BULLISH", "score": 100, "confidence": "HIGH"},
        [evidence("ev-1", "Trend is BULLISH"), evidence("ev-2", "Trend is BEARISH")],
    )
    assert result["reasoning_confidence"] == 90.0
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["confidence"] == "HIGH"
