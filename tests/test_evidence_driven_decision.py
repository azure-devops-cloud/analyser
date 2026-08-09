from services.decision_service import DecisionService
from services.evidence_service import EvidenceService

def _gold_market():
    return {"name":"GOLD","price":4000,"trend":"BULLISH","rsi":28,"daily_change":1.8,"volatility":18,"signal":"BUY"}

def test_evidence_service_builds_auditable_market_signals():
    evidence=EvidenceService().build(_gold_market(),sentiment={"positive":8,"negative":2},calendar_events=[{"name":"CPI"}],fact_validation={"confidence_score":70})
    assert len(evidence)>=6
    assert all(item.evidence_id.startswith("ev-") for item in evidence)
    assert {item.kind for item in evidence}>={"technical","momentum","risk","sentiment","macro","validation"}

def test_decision_preserves_legacy_score_without_evidence():
    result=DecisionService().analyze(_gold_market(),sentiment={"positive":8,"negative":2})
    assert result["score"]==95
    assert result["bias"]=="BULLISH"

def test_decision_contains_evidence_without_changing_legacy_score():
    market=_gold_market(); sentiment={"positive":8,"negative":2}; evidence=EvidenceService().build(market,sentiment)
    legacy_result=DecisionService().analyze(market,sentiment=sentiment); evidence_result=DecisionService().analyze(market,sentiment=sentiment,evidence=evidence)
    assert evidence_result["score"]==legacy_result["score"]
    assert evidence_result["bias"]==legacy_result["bias"]
    assert evidence_result["evidence"]["count"]==len(evidence)
    assert evidence_result["evidence"]["items"]

def test_evidence_is_descriptive_and_cannot_change_score():
    market=_gold_market(); sentiment={"positive":8,"negative":2}; baseline=DecisionService().analyze(market,sentiment=sentiment)
    evidence=EvidenceService().build(market,sentiment=sentiment,calendar_events=[{"name":"CPI"}],fact_validation={"confidence_score":95})
    with_evidence=DecisionService().analyze(market,sentiment=sentiment,evidence=evidence)
    assert baseline["score"]==95
    assert with_evidence["score"]==baseline["score"]
    assert with_evidence["bias"]==baseline["bias"]
    assert with_evidence["evidence"]["count"]==len(evidence)
