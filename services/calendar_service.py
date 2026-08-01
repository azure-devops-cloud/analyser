import feedparser
from datetime import datetime


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

                rss = feedparser.parse(feed)

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

            except Exception:
                pass

        return events
