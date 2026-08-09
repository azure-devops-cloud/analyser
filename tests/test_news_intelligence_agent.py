import pytest
from datetime import datetime, timezone

from agents.news_intelligence_agent import NewsIntelligenceAgent
from services.news_intelligence_service import NewsIntelligenceService


NOW = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)


def articles():
    return [
        {
            "title": "Fed signals rate cut as inflation falls",
            "link": "https://fed.example/story-1",
            "published": "2026-08-08T10:00:00Z",
            "source": "fed",
            "category": "fed",
        },
        {
            "title": "Fed signals rate cut as inflation falls",
            "link": "https://fed.example/story-1",
            "published": "2026-08-08T10:00:00Z",
            "source": "fed",
            "category": "fed",
        },
        {
            "title": "Kubernetes releases maintenance update",
            "link": "https://k8s.example/story-2",
            "published": "2026-08-01T10:00:00Z",
            "source": "k8s",
            "category": "opensource",
        },
    ]


def test_service_deduplicates_and_ranks_actionable_news():
    result = NewsIntelligenceService().analyze(
        articles(),
        source_trust={"fed": 1.0, "k8s": 0.8},
        now=NOW,
    )

    assert len(result) == 2
    assert result[0]["impact"] == "HIGH"
    assert result[0]["actionability"] > 0
    assert result[0]["evidence_id"].startswith("news-")
    assert result[0]["why_it_matters"]
    assert result[0]["actions"]


def test_service_ignores_malformed_articles():
    result = NewsIntelligenceService().analyze(
        [None, {}, {"title": "missing link"}, {"link": "missing title"}],
        now=NOW,
    )
    assert result == []


def test_llm_can_enrich_prose_but_cannot_change_scores():
    def fake_llm(item):
        return {
            "why_it_matters": "LLM explanation",
            "actions": ["Review source", "Check price"],
            "importance": 0,
            "impact": "LOW",
        }

    result = NewsIntelligenceService(llm_client=fake_llm).analyze(
        [articles()[0]], source_trust={"fed": 1.0}, now=NOW
    )[0]
    assert result["why_it_matters"] == "LLM explanation"
    assert result["actions"] == ["Review source", "Check price"]
    assert result["impact"] == "HIGH"
    assert result["importance"] > 0


def test_agent_writes_intelligence_to_context():
    context = {"news": [articles()[0]]}
    result = NewsIntelligenceAgent(source_trust={"fed": 1.0}).run(context)
    assert result.status == "success"
    assert context["news_intelligence"][0]["evidence_id"].startswith("news-")
