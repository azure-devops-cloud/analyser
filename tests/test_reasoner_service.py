from agents.reasoner_agent import ReasonerAgent
from services.reasoner_service import ReasonerService


def evidence(asset="GOLD"):
    return [
        {
            "evidence_id": "ev-1",
            "kind": "technical",
            "claim": "Trend is BULLISH",
            "value": "BULLISH",
            "strength": 0.9,
            "metadata": {"asset": asset},
        },
        {
            "evidence_id": "ev-2",
            "kind": "momentum",
            "claim": "Daily change is +1.8%",
            "value": 1.8,
            "strength": 0.7,
            "metadata": {"asset": asset},
        },
        {
            "evidence_id": "ev-3",
            "kind": "sentiment",
            "claim": "Sentiment is positive",
            "value": {"positive": 8, "negative": 2},
            "strength": 0.8,
            "metadata": {"asset": asset},
        },
        {
            "evidence_id": "ev-4",
            "kind": "technical",
            "claim": "Trend is BEARISH",
            "value": "BEARISH",
            "strength": 0.9,
            "metadata": {"asset": "BITCOIN"},
        },
    ]


def test_reasoner_returns_structured_evidence_packet_without_changing_decision():
    decision = {"name": "GOLD", "bias": "BULLISH", "score": 100, "confidence": "HIGH"}

    result = ReasonerService().analyze(decision, evidence())

    assert result["asset"] == "GOLD"
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["evidence_count"] == 3
    assert result["evidence_by_kind"] == {"technical": 1, "momentum": 1, "sentiment": 1}
    assert result["stance"] == "supporting"
    assert len(result["supporting"]) == 3
    assert result["opposing"] == []


def test_reasoner_does_not_use_other_asset_evidence():
    decision = {"name": "GOLD", "bias": "BULLISH", "score": 100, "confidence": "HIGH"}

    result = ReasonerService().analyze(decision, evidence())

    assert "BITCOIN" not in result["reasoning"]
    assert result["evidence_count"] == 3


def test_reasoner_agent_exposes_packet_in_context():
    agent = ReasonerAgent()
    context = {
        "decisions": [{"name": "GOLD", "bias": "BULLISH", "score": 100, "confidence": "HIGH"}],
        "evidence": evidence(),
    }

    result = agent.run(context)

    assert result.status == "success"
    assert result.data[0]["asset"] == "GOLD"
    assert result.data[0]["score"] == 100
    assert context["reasoning"][0]["asset"] == "GOLD"
