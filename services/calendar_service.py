import feedparser
import requests
from datetime import datetime
from services.logger import get_logger


logger = get_logger(__name__)


class CalendarService:

    FEEDS = [
        "https://www.forexfactory.com/ff_calendar_thisweek.xml"
    ]

    KEYWORDS = [
        "Fed",
        "FOMC",
        "CPI",
        "PPI",
        "NFP",
        "Payroll",
        "Interest Rate",
        "GDP",
        "Core PCE",
        "RBI"
    ]

    def get_events(self):

        events = []

        for feed in self.FEEDS:

            try:

                response = requests.get(
                    feed,
                    timeout=20,
                    headers={"User-Agent": "MarketMind-AI/0.2"},
                )
                response.raise_for_status()
                rss = feedparser.parse(response.content)

                for entry in rss.entries:

                    title = getattr(entry, "title", "")

                    matched = any(
                        keyword.lower() in title.lower()
                        for keyword in self.KEYWORDS
                    )

                    if not matched:
                        continue

                    events.append(
                        {
                            "title": title,
                            "published": getattr(
                                entry,
                                "published",
                                datetime.utcnow().isoformat()
                            ),
                            "link": getattr(entry, "link", "")
                        }
                    )

            except Exception as ex:
                logger.warning("Calendar feed %s failed: %s", feed, ex)

        return events
