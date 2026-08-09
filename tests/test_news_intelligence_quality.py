from datetime import datetime, timezone

from services.news_intelligence_service import NewsIntelligenceService


def test_news_intelligence_corroborates_same_story_across_sources():
    service = NewsIntelligenceService()
    result = service.analyze(
        [
            {
                "title": "Fed raises rates as inflation remains high",
                "link": "https://a.example/1",
                "source": "Source A",
                "published": "2026-08-09T00:00:00Z",
            },
            {
                "title": "Fed raises rates as inflation remains high, reports Source B",
                "link": "https://b.example/1",
                "source": "Source B",
                "published": "2026-08-09T00:05:00Z",
            },
        ],
        now=datetime(2026, 8, 9, 1, tzinfo=timezone.utc),
    )

    assert len(result) == 2
    assert {item["corroboration_count"] for item in result} == {2}
    assert all(set(item["corroborating_sources"]) == {"Source A", "Source B"} for item in result)


def test_news_intelligence_detects_conflicting_directional_coverage():
    service = NewsIntelligenceService()
    result = service.analyze(
        [
            {
                "title": "Fed raises rates, boosting the dollar",
                "link": "https://a.example/1",
                "source": "Source A",
                "published": "2026-08-09T00:00:00Z",
            },
            {
                "title": "Fed raises rates, dollar falls after decision",
                "link": "https://b.example/1",
                "source": "Source B",
                "published": "2026-08-09T00:05:00Z",
            },
        ],
        now=datetime(2026, 8, 9, 1, tzinfo=timezone.utc),
    )

    assert any(item["contradiction_detected"] for item in result)
    assert any("conflicting" in item["why_it_matters"].lower() for item in result)
    assert any("discrepancy" in action.lower() for item in result for action in item["actions"])


def test_news_intelligence_marks_stale_news_and_caps_its_score():
    service = NewsIntelligenceService()
    result = service.analyze(
        [
            {
                "title": "Fed announces rate decision",
                "link": "https://a.example/1",
                "source": "Source A",
                "published": "2026-07-01T00:00:00Z",
            }
        ],
        now=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )

    item = result[0]
    assert item["temporal_status"] == "STALE"
    assert item["freshness"] <= 0.05
    assert item["score"] <= 39.9
    assert item["impact"] == "LOW"


def test_news_intelligence_normalizes_source_trust_percentages():
    service = NewsIntelligenceService()
    result = service.analyze(
        [
            {
                "title": "Fed announces rate decision",
                "link": "https://a.example/1",
                "source": "Trusted Source",
                "published": "2026-08-09T00:00:00Z",
            }
        ],
        source_trust={"Trusted Source": 95},
        now=datetime(2026, 8, 9, 1, tzinfo=timezone.utc),
    )

    assert result[0]["source_trust"] == 0.95
    assert result[0]["score"] > 50
