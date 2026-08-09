from services.verification_service import VerificationService


def test_verification_requires_more_evidence_for_single_source():
    result = VerificationService().verify(
        articles=[{"title": "Fed holds rates", "source": "https://example.com/a"}],
        evidence=[{"evidence_id": "ev-1"}],
        intelligence=[{"title": "Fed holds rates", "corroboration_count": 1}],
        source_trust={"example.com": 0.8},
    )

    assert result["status"] == "partially_verified"
    assert "single_source" in result["checks"]
    assert result["confidence_score"] < 100
    assert "independent source" in result["recommended_action"]


def test_verification_detects_conflicting_intelligence():
    result = VerificationService().verify(
        articles=[
            {"title": "Rates rise", "source": "https://a.example/news"},
            {"title": "Rates fall", "source": "https://b.example/news"},
        ],
        evidence=[{"evidence_id": "ev-1"}],
        intelligence=[
            {"title": "Rates rise", "corroboration_count": 1, "contradiction": True},
        ],
    )

    assert result["status"] == "needs_verification"
    assert result["contradiction_count"] == 1
    assert "contradictory_sources" in result["checks"]
    assert "conflicting sources" in result["recommended_action"]


def test_verification_normalizes_source_trust_scales():
    result = VerificationService().verify(
        articles=[
            {"title": "Gold rises", "source": "https://a.example/news"},
            {"title": "Gold rises", "source": "https://b.example/news"},
        ],
        evidence=[{"evidence_id": "ev-1"}],
        intelligence=[{"title": "Gold rises", "corroboration_count": 2}],
        source_trust={"a.example": 0.9, "b.example": 80},
    )

    assert result["status"] == "verified"
    assert result["average_source_trust"] == 85.0
    assert result["confidence_score"] <= 100


def test_verification_degrades_without_evidence():
    result = VerificationService().verify(
        articles=[{"title": "Oil moves", "source": "https://example.com/oil"}],
        evidence=[],
        intelligence=[],
    )

    assert result["status"] == "degraded"
    assert "no_evidence" in result["checks"]
    assert result["confidence_score"] < 100
