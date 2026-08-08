from services.llm_reasoner_service import LLMReasonerService


def packet():
    return {
        "asset": "GOLD",
        "bias": "BULLISH",
        "score": 100,
        "evidence_count": 2,
        "stance": "supporting",
        "supporting": [
            {"evidence_id": "ev-1", "claim": "Trend is BULLISH"},
            {"evidence_id": "ev-2", "claim": "Daily change is +1.8%"},
        ],
        "opposing": [],
    }


def test_llm_reasoner_falls_back_without_client():
    result = LLMReasonerService().synthesize(packet())

    assert result["asset"] == "GOLD"
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["cited_evidence_ids"] == ["ev-1", "ev-2"]


def test_llm_reasoner_filters_unknown_citations():
    service = LLMReasonerService(client=lambda prompt: {
        "summary": "Bullish",
        "key_points": ["Trend supports the decision"],
        "cited_evidence_ids": ["ev-1", "hallucinated-id"],
    })

    result = service.synthesize(packet())

    assert result["cited_evidence_ids"] == ["ev-1"]
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"


def test_llm_failure_uses_deterministic_fallback():
    service = LLMReasonerService(client=lambda prompt: (_ for _ in ()).throw(RuntimeError("provider down")))

    result = service.synthesize(packet())

    assert result["asset"] == "GOLD"
    assert result["score"] == 100
    assert result["bias"] == "BULLISH"
    assert result["cited_evidence_ids"] == ["ev-1", "ev-2"]
