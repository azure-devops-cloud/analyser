import main
from agents.manager_agent import ManagerAgent
from agents.news_agent import NewsAgent
from agents.summary_agent import SummaryAgent
from models.context import AgentContext
from services.database_service import DatabaseService
from services.market_data_service import MarketService
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

    assert len(results) == 10
    assert all(result.status == "success" for result in results)
    assert context.market
    assert context.news
    assert context.news_sentiment
    assert context.decisions


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
