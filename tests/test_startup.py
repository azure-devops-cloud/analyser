import main
from agents.manager_agent import ManagerAgent
from agents.news_agent import NewsAgent
from agents.summary_agent import SummaryAgent
from agents.deduplication_agent import DeduplicationAgent
from agents.ranking_agent import RankingAgent
from agents.fact_validation_agent import FactValidationAgent
from models.context import AgentContext
from services.telegram_service import send_message
from services.database_service import DatabaseService
from services.market_data_service import MarketService
from services.news_storage_service import NewsStorageService
from services.alert_service import AlertService
from services.market_history_service import MarketHistoryService
from services.news_history_service import NewsHistoryService
from services.telegram_service import send_message


def test_database_service_initializes_expected_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "marketmind.db"
    monkeypatch.setattr("services.database_service.DATABASE_PATH", db_path)

    db = DatabaseService()
    db.initialize()

    tables = {row[0] for row in db.health_check()}

    assert "news" in tables
    assert "market_snapshot" in tables
    assert "alerts" in tables

    db.close()


def test_send_message_skips_when_credentials_are_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    result = send_message("test message")

    assert result is False


def test_manager_agent_run_smoke_pipeline(tmp_path, monkeypatch):
    db_path = tmp_path / "marketmind.db"
    monkeypatch.setattr("services.database_service.DATABASE_PATH", db_path)

    monkeypatch.setattr(
        "services.rss_service.RSSService.get_feed",
        lambda url: [
            {
                "title": "Fed rate cut boosts growth outlook",
                "link": "https://example.com/news/1",
                "published": "2026-08-01T00:00:00Z"
            }
        ]
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
                "daily_change": 1.4
            }
        ]
    )

    monkeypatch.setattr(
        "services.calendar_service.CalendarService.get_events",
        lambda self: [
            {
                "title": "Fed FOMC Meeting",
                "published": "2026-08-01T00:00:00Z",
                "link": "https://example.com/calendar/1"
            }
        ]
    )

    monkeypatch.setattr(
        "services.sentiment_service.SentimentService.analyze",
        lambda self, title: {
            "sentiment": "POSITIVE",
            "score": 2
        }
    )

    manager = ManagerAgent()
    results, context = manager.run()

    assert len(results) == 16
    assert all(result.status == "success" for result in results)
    assert context.market
    assert context.news
    assert context.news_sentiment
    assert context.decisions
    assert context.reasoning


def test_summary_agent_builds_human_readable_summary():
    context = AgentContext()
    context.news = [
        {
            "title": "Fed rate cut boosts growth outlook",
            "category": "FED",
            "impact": "HIGH",
            "sentiment": "POSITIVE",
            "sentiment_score": 2
        },
        {
            "title": "Crypto selloff fears rise",
            "category": "CRYPTO",
            "impact": "MEDIUM",
            "sentiment": "NEGATIVE",
            "sentiment_score": 1
        }
    ]
    context.market = [
        {
            "name": "BITCOIN",
            "trend": "BULLISH",
            "signal": "BUY",
            "daily_change": 1.2,
            "rsi": 66
        }
    ]
    context.news_sentiment = {"positive": 1, "negative": 1, "neutral": 0}
    context.decisions = [
        {
            "name": "BITCOIN",
            "bias": "BULLISH",
            "score": 82,
            "confidence": "HIGH",
            "reasons": ["Positive daily momentum"]
        }
    ]

    result = SummaryAgent().run(context)

    assert result.status == "success"
    assert result.agent == "summary_agent"
    assert result.data["headline"]
    assert result.data["summary"]
    assert result.data["market_bias"] == "bullish"
    assert result.data["market_posture"] == "Bullish"
    assert result.data["top_opportunity"] == "BITCOIN"
    assert result.data["watchlist"] == "BITCOIN"
    assert result.data["risk_caveat"]
    assert result.data["risk_watch"] == result.data["risk_caveat"]
    assert result.data["action_recommendation"]
    assert "BITCOIN" in result.data["summary"]


def test_news_agent_continues_when_one_feed_fails(monkeypatch, tmp_path):
    db_path = tmp_path / "marketmind.db"
    monkeypatch.setattr("services.database_service.DATABASE_PATH", db_path)

    monkeypatch.setattr(
        "agents.news_agent.RSS_FEEDS",
        {
            "good": ["https://good.example/feed.xml"],
            "bad": ["https://bad.example/feed.xml"]
        }
    )

    def fake_get_feed(url):
        if url == "https://bad.example/feed.xml":
            raise RuntimeError("feed unavailable")

        return [
            {
                "title": "Fed rate cut boosts growth outlook",
                "link": "https://example.com/news/1",
                "published": "2026-08-01T00:00:00Z"
            }
        ]

    monkeypatch.setattr(
        "services.rss_service.RSSService.get_feed",
        fake_get_feed
    )

    agent = NewsAgent()
    context = AgentContext()
    result = agent.run(context)

    assert result.status == "success"
    assert result.count == 1
    assert len(context.news) == 1


def test_market_service_continues_when_one_symbol_fails(monkeypatch):
    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, period, interval, auto_adjust=False):
            if self.symbol == "BTC-USD":
                raise RuntimeError("market data unavailable")

            import pandas as pd
            index = pd.date_range("2026-07-01", periods=3, freq="D")
            return pd.DataFrame(
                {
                    "Close": [100, 101, 102],
                    "Open": [99, 100, 101],
                    "High": [101, 102, 103],
                    "Low": [98, 99, 100],
                    "Volume": [1000, 1000, 1000]
                },
                index=index
            )

    monkeypatch.setattr("services.market_data_service.yf.Ticker", FakeTicker)
    monkeypatch.setattr(
        "services.market_data_service.TechnicalIndicatorService.calculate",
        lambda data: {
            "price": 102,
            "trend": "BULLISH",
            "signal": "BUY",
            "rsi": 66,
            "volatility": 28
        }
    )

    service = MarketService()
    data = service.get_market_data()

    assert len(data) == len(service.SYMBOLS) - 1
    assert all(item["symbol"] != "BTC-USD" for item in data)


def test_main_supports_dry_run(monkeypatch, capsys):
    class FakeResult:
        def __init__(self, agent, status, data=None, count=0):
            self.agent = agent
            self.status = status
            self.data = data or {}
            self.count = count

    monkeypatch.setattr(
        "main.DatabaseService",
        lambda: type(
            "FakeDB",
            (),
            {
                "initialize": lambda self: None,
                "health_check": lambda self: [("news",), ("market_snapshot",), ("alerts",)],
                "close": lambda self: None,
            }
        )()
    )

    monkeypatch.setattr(
        "main.ManagerAgent",
        lambda: type(
            "FakeManager",
            (),
            {
                "run": lambda self: (
                    [
                        FakeResult("news_agent", "success", {"total_checked": 1, "analysis": {"categories": {"fed": 1}, "impact": {"HIGH": 1}}}, 1),
                        FakeResult("market_agent", "success", [{"name": "BITCOIN", "price": 100, "daily_change": 1.2, "trend": "BULLISH", "signal": "BUY", "rsi": 55}], 1),
                    ],
                    {}
                )
            }
        )()
    )

    sent = []

    def fake_send(message):
        sent.append(message)

    monkeypatch.setattr("main.send_message", fake_send)

    exit_code = main.main(["--dry-run"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert sent == []
    assert "MarketMind AI" in captured.out
    assert "Executive Brief" in captured.out
    assert "Tables : 3" in captured.out


def test_main_supports_bounded_loop_mode(monkeypatch, capsys):
    class FakeResult:
        def __init__(self, agent, status, data=None, count=0):
            self.agent = agent
            self.status = status
            self.data = data or {}
            self.count = count

    class FakeManager:
        def __init__(self):
            self.run_count = 0

        def run(self):
            self.run_count += 1
            return (
                [
                    FakeResult(
                        "summary_agent",
                        "success",
                        {
                            "headline": "Loop run",
                            "action_recommendation": "Action",
                            "risk_watch": "Risk",
                            "top_opportunity": "BITCOIN",
                            "market_posture": "Bullish",
                        },
                        1,
                    )
                ],
                {},
            )

    monkeypatch.setattr(
        "main.DatabaseService",
        lambda: type(
            "FakeDB",
            (),
            {
                "initialize": lambda self: None,
                "health_check": lambda self: [("news",), ("market_snapshot",), ("alerts",)],
                "close": lambda self: None,
            }
        )()
    )

    monkeypatch.setattr("main.ManagerAgent", FakeManager)

    exit_code = main.main(["--dry-run", "--loop", "--max-runs", "2", "--interval", "0"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Loop run" in captured.out
    assert captured.out.count("Loop run") == 2


def test_main_supports_json_dry_run(monkeypatch, capsys):
    class FakeResult:
        def __init__(self, agent, status, data=None, count=0, errors=None):
            self.agent = agent
            self.status = status
            self.data = data or {}
            self.count = count
            self.errors = errors or []

    monkeypatch.setattr(
        "main.DatabaseService",
        lambda: type(
            "FakeDB",
            (),
            {
                "initialize": lambda self: None,
                "health_check": lambda self: [("news",), ("market_snapshot",)],
                "close": lambda self: None,
            },
        )(),
    )
    monkeypatch.setattr(
        "main.ManagerAgent",
        lambda: type(
            "FakeManager",
            (),
            {
                "run": lambda self: (
                    [FakeResult("market_agent", "failed", errors=["provider unavailable"])],
                    {},
                )
            },
        )(),
    )

    assert main.main(["--dry-run", "--format", "json"]) == 0
    payload = __import__("json").loads(capsys.readouterr().out)

    assert payload["workflow_health"] == "degraded"
    assert payload["failed_agents"] == ["market_agent"]
    assert payload["agents"]["market_agent"]["errors"] == ["provider unavailable"]


def test_deduplication_and_ranking_use_source_priority_for_accuracy():
    context = AgentContext()
    context.news = [
        {
            "title": "Fed rate cut boosts growth outlook",
            "link": "https://example.com/a",
            "summary": "Fed rate cut boosts growth outlook",
            "source_priority": 1,
            "sentiment_score": 2,
            "impact_score": 85,
            "impact": "HIGH",
        },
        {
            "title": "Fed rate cut boosts growth outlook",
            "link": "https://example.com/b",
            "summary": "Fed rate cut boosts growth outlook",
            "source_priority": 5,
            "sentiment_score": 2,
            "impact_score": 90,
            "impact": "HIGH",
        },
        {
            "title": "Crypto rally accelerates",
            "link": "https://example.com/c",
            "summary": "Crypto rally accelerates",
            "source_priority": 2,
            "sentiment_score": 1,
            "impact_score": 40,
            "impact": "MEDIUM",
        },
    ]

    dedupe_result = DeduplicationAgent().run(context)
    assert dedupe_result.status == "success"
    assert dedupe_result.count == 2

    ranked = RankingAgent().run(context)
    assert ranked.status == "success"
    assert ranked.data["top_story"]["link"] == "https://example.com/b"
    assert ranked.data["top_score"] >= 100


def test_summary_agent_uses_fact_validation_confidence_for_cautious_action():
    context = AgentContext()
    context.news = [
        {
            "title": "Fed rate cut boosts growth outlook",
            "category": "FED",
            "impact": "HIGH",
            "sentiment": "POSITIVE",
            "sentiment_score": 2,
            "source_priority": 1,
            "link": "https://example.com/one",
        }
    ]
    context.market = [
        {
            "name": "BITCOIN",
            "trend": "BULLISH",
            "signal": "BUY",
            "daily_change": 1.2,
            "rsi": 66,
        }
    ]
    context.news_sentiment = {"positive": 1, "negative": 0, "neutral": 0}
    context.decisions = [
        {
            "name": "BITCOIN",
            "bias": "BULLISH",
            "score": 82,
        }
    ]
    context.fact_validation = {
        "confidence_score": 35,
        "verification_status": "needs_more_sources",
        "evidence_count": 0,
    }

    result = SummaryAgent().run(context)

    assert result.status == "success"
    assert "wait for more evidence" in result.data["action_recommendation"].lower()
    assert "hold" in result.data["action_recommendation"].lower()


def test_send_message_respects_confidence_threshold(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    calls = []

    def fake_post(url, json=None, timeout=30):
        calls.append(json)

        class Response:
            status_code = 200
            text = "ok"

        return Response()

    monkeypatch.setattr("services.telegram_service.requests.post", fake_post)

    assert send_message("high-confidence message", confidence_score=85, threshold=80) is True
    assert send_message("low-confidence message", confidence_score=30, threshold=80) is False
    assert len(calls) == 1


def test_ranking_agent_uses_persistent_source_trust_map():
    context = AgentContext()
    context.source_trust_map = {
        "https://example.com/credible": 95,
        "https://example.com/noisy": 35,
    }
    context.news = [
        {
            "title": "Fed rate cut boosts growth outlook",
            "link": "https://example.com/noisy",
            "summary": "Fed rate cut boosts growth outlook",
            "source_priority": 1,
            "sentiment_score": 2,
            "impact_score": 85,
            "impact": "HIGH",
        },
        {
            "title": "Fed rate cut boosts growth outlook",
            "link": "https://example.com/credible",
            "summary": "Fed rate cut boosts growth outlook",
            "source_priority": 3,
            "sentiment_score": 2,
            "impact_score": 88,
            "impact": "HIGH",
        },
    ]

    result = RankingAgent().run(context)

    assert result.status == "success"
    assert result.data["top_story"]["link"] == "https://example.com/credible"


def test_fact_validation_uses_distinct_sources_before_deduplication():
    context = AgentContext()
    context.news = [
        {
            "title": "Fed rate cut boosts growth outlook",
            "source": "https://source-one.example/feed.xml",
        },
        {
            "title": "Fed rate cut boosts growth outlook",
            "source": "https://source-two.example/feed.xml",
        },
    ]

    result = FactValidationAgent().run(context)

    assert result.status == "success"
    assert result.data["verification_status"] == "validated"
    assert result.data["evidence_count"] == 2
    assert result.data["confidence_score"] == 70


def test_news_storage_ignores_revised_title_at_existing_url(tmp_path, monkeypatch):
    db_path = tmp_path / "marketmind.db"
    monkeypatch.setattr("services.database_service.DATABASE_PATH", db_path)
    storage = NewsStorageService()

    first = storage.save_news([
        {"title": "Original headline", "link": "https://example.com/story"}
    ])
    revised = storage.save_news([
        {"title": "Revised headline", "link": "https://example.com/story"}
    ])

    storage.close()

    assert len(first) == 1
    assert revised == []


def test_alerts_are_actionable_and_deduplicated_per_day(tmp_path, monkeypatch):
    monkeypatch.setattr("services.database_service.DATABASE_PATH", tmp_path / "marketmind.db")
    service = AlertService()
    decisions = [{"name": "BITCOIN", "bias": "BULLISH", "score": 82, "trend": "BULLISH", "rsi": 60}]

    created = service.create_actionable_alerts(decisions)
    duplicate = service.create_actionable_alerts(decisions)
    service.close()

    assert created[0]["category"] == "BUY_WATCH"
    assert duplicate == []


def test_market_history_calculates_snapshot_change(tmp_path, monkeypatch):
    monkeypatch.setattr("services.database_service.DATABASE_PATH", tmp_path / "marketmind.db")
    service = MarketHistoryService()
    first = service.record([{"name": "BITCOIN", "symbol": "BTC-USD", "price": 100, "daily_change": 1}])
    second = service.record([{"name": "BITCOIN", "symbol": "BTC-USD", "price": 110, "daily_change": 2}])
    recent = service.recent()
    service.close()

    assert first[0]["snapshot_change_pct"] is None
    assert second[0]["snapshot_change_pct"] == 10.0
    assert len(recent) == 2


def test_news_history_reports_persisted_articles(tmp_path, monkeypatch):
    monkeypatch.setattr("services.database_service.DATABASE_PATH", tmp_path / "marketmind.db")
    storage = NewsStorageService()
    storage.save_news([
        {
            "title": "Inflation data update",
            "link": "https://example.com/inflation",
            "category": "FED",
            "source": "https://example.com/feed",
        }
    ])
    storage.close()
    history = NewsHistoryService()
    summary = history.summary()
    history.close()

    assert summary["total_articles"] == 1
    assert summary["articles_last_24h"] == 1
    assert summary["categories_last_24h"] == {"FED": 1}


def test_main_requires_telegram_credentials_for_live_run(monkeypatch, capsys):
    class FakeResult:
        def __init__(self, agent, status, data=None, count=0):
            self.agent = agent
            self.status = status
            self.data = data or {}
            self.count = count

    monkeypatch.setattr(
        "main.DatabaseService",
        lambda: type(
            "FakeDB",
            (),
            {
                "initialize": lambda self: None,
                "health_check": lambda self: [("news",), ("market_snapshot",), ("alerts",)],
                "close": lambda self: None,
            }
        )()
    )

    monkeypatch.setattr(
        "main.ManagerAgent",
        lambda: type(
            "FakeManager",
            (),
            {
                "run": lambda self: (
                    [
                        FakeResult("news_agent", "success", {"total_checked": 1, "analysis": {"categories": {"fed": 1}, "impact": {"HIGH": 1}}}, 1)
                    ],
                    {}
                )
            }
        )()
    )

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    exit_code = main.main([])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "TELEGRAM_BOT_TOKEN" in captured.err
