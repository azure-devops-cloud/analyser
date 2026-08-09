from agents.manager_agent import ManagerAgent


def test_manager_integrates_news_intelligence_before_downstream_agents(monkeypatch, tmp_path):
    monkeypatch.setattr("services.database_service.DATABASE_PATH", tmp_path / "marketmind.db")
    monkeypatch.setattr(
        "services.rss_service.RSSService.get_feed",
        lambda url: [
            {
                "title": "Fed cuts rates and markets rise",
                "link": "https://example.com/fed",
                "published": "2026-08-08T00:00:00Z",
                "source": "Example News",
            },
            {
                "title": "Routine market commentary",
                "link": "https://example.com/routine",
                "published": "2026-08-08T00:00:00Z",
                "source": "Example News",
            },
        ],
    )
    monkeypatch.setattr(
        "services.market_data_service.MarketService.get_market_data",
        lambda self: [
            {
                "name": "BITCOIN",
                "price": 62000,
                "trend": "BULLISH",
                "signal": "BUY",
                "rsi": 66,
                "volatility": 28,
                "daily_change": 1.4,
            }
        ],
    )
    monkeypatch.setattr(
        "services.calendar_service.CalendarService.get_events",
        lambda self: [],
    )
    monkeypatch.setattr(
        "services.sentiment_service.SentimentService.analyze",
        lambda self, title: {"sentiment": "POSITIVE", "score": 2},
    )

    results, context = ManagerAgent().run()

    assert all(result.status == "success" for result in results)
    assert context.news_intelligence
    assert context.news_intelligence[0]["evidence_id"].startswith("news-")
    assert context.news_intelligence[0]["why_it_matters"]
    assert context.news_intelligence[0]["actions"]

    names = [result.agent for result in results]
    assert names.index("news_intelligence_agent") < names.index("decision_agent")
    assert context.decisions
    assert context.reasoning


def test_news_intelligence_failure_does_not_block_manager_pipeline(monkeypatch, tmp_path):
    monkeypatch.setattr("services.database_service.DATABASE_PATH", tmp_path / "marketmind.db")
    monkeypatch.setattr(
        "services.rss_service.RSSService.get_feed",
        lambda url: [{
            "title": "Fed rate decision",
            "link": "https://example.com/fed",
            "published": "2026-08-08T00:00:00Z",
        }],
    )
    monkeypatch.setattr(
        "services.market_data_service.MarketService.get_market_data",
        lambda self: [{
            "name": "BITCOIN",
            "price": 62000,
            "trend": "BULLISH",
            "signal": "BUY",
            "rsi": 66,
            "volatility": 28,
            "daily_change": 1.4,
        }],
    )
    monkeypatch.setattr("services.calendar_service.CalendarService.get_events", lambda self: [])
    monkeypatch.setattr(
        "services.sentiment_service.SentimentService.analyze",
        lambda self, title: {"sentiment": "POSITIVE", "score": 2},
    )

    from services.news_intelligence_service import NewsIntelligenceService
    monkeypatch.setattr(
        NewsIntelligenceService,
        "analyze",
        lambda self, articles, source_trust=None: (_ for _ in ()).throw(RuntimeError("intelligence unavailable")),
    )

    results, context = ManagerAgent().run()

    intelligence_result = next(r for r in results if r.agent == "news_intelligence_agent")
    assert intelligence_result.status == "failed"
    assert context.errors
    assert context.decisions
    assert context.reasoning
