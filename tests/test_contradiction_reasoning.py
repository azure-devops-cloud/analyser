from services.reasoner_service import ReasonerService


def ev(evidence_id, claim, kind="technical", asset="GOLD"):
    return {
        "evidence_id": evidence_id,
        "asset": asset,
        "kind": kind,
        "claim": claim,
        "value": 1,
        "strength": 0.8,
        "source": "test",
        "metadata": {},
    }


def test_contradictory_same_kind_evidence_is_flagged_without_changing_decision():
    decision = {"name": "GOLD", "bias": "BULLISH", "score": 90, "confidence": "HIGH"}
    result = ReasonerService().analyze(decision, [
        ev("ev-1", "Trend is BULLISH"),
        ev("ev-2", "Trend is BEARISH"),
    ])

    assert result["evidence_status"] == "CONFLICTED"
    assert result["contradictions"][0]["evidence_ids"] == ["ev-1", "ev-2"]
    assert result["score"] == 90
    assert result["bias"] == "BULLISH"


def test_different_assets_do_not_create_cross_asset_contradiction():
    decision = {"name": "GOLD", "bias": "BULLISH", "score": 90, "confidence": "HIGH"}
    result = ReasonerService().analyze(decision, [
        ev("ev-1", "Trend is BULLISH", asset="GOLD"),
        ev("ev-2", "Trend is BEARISH", asset="BITCOIN"),
    ])

    assert result["contradictions"] == []
    assert result["evidence_status"] == "SUPPORTED"


def test_contradiction_preserves_authoritative_decision_fields():
    decision = {"name": "GOLD", "bias": "BULLISH", "score": 100, "confidence": "HIGH"}
    result = ReasonerService().analyze(decision, [
        ev("ev-1", "Trend is BULLISH"),
        ev("ev-2", "Trend is BEARISH"),
        ev("ev-3", "Trend is BEARISH"),
    ])

    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["confidence"] == "HIGH"
    assert result["contradictions"][0]["severity"] == "HIGH"
