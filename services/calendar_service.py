from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

from services.logger import get_logger

logger = get_logger(__name__)


class CalendarService:
    """Collect macro events with provider health and official-source fallbacks."""

    FEEDS = [
        ("forexfactory", "https://www.forexfactory.com/ff_calendar_thisweek.xml"),
    ]

    OFFICIAL_SOURCES = [
        ("bls", "https://www.bls.gov/schedule/2026/"),
        ("federal_reserve", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"),
        ("bea", "https://www.bea.gov/news/schedule/full"),
    ]

    KEYWORDS = [
        "Fed", "FOMC", "CPI", "Consumer Price Index", "PPI", "Producer Price Index",
        "NFP", "Payroll", "Employment", "Interest Rate", "GDP", "Core PCE",
        "Personal Income", "Personal Consumption Expenditures", "PCE", "RBI",
        "Retail Sales", "Unemployment", "Jobless Claims", "Nonfarm Payrolls",
    ]

    def __init__(self):
        self.status = "unknown"
        self.providers = {}

    @staticmethod
    def _matches(title):
        normalized = " ".join(str(title).split()).lower()
        return any(keyword.lower() in normalized for keyword in CalendarService.KEYWORDS)

    def _feed_events(self, name, url):
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "MarketMind-AI/0.3"},
        )
        response.raise_for_status()
        rss = feedparser.parse(response.content)
        events = []
        for entry in rss.entries:
            title = getattr(entry, "title", "")
            if self._matches(title):
                events.append({
                    "title": title,
                    "published": getattr(entry, "published", datetime.utcnow().isoformat()),
                    "link": getattr(entry, "link", ""),
                    "source": name,
                })
        return events

    def _official_events(self, name, url):
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "MarketMind-AI/0.3"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        events = []

        for row in soup.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            text = " | ".join(cell for cell in cells if cell)
            if not text or not self._matches(text):
                continue

            title = next((cell for cell in cells if self._matches(cell)), text)
            events.append({
                "title": title,
                "published": cells[0] if cells else datetime.utcnow().isoformat(),
                "link": url,
                "source": name,
            })

        # Some official pages use headings/list items instead of tables.
        if not events:
            for element in soup.find_all(["li", "p", "h3", "h4"]):
                text = element.get_text(" ", strip=True)
                if text and self._matches(text):
                    events.append({
                        "title": text,
                        "published": datetime.utcnow().isoformat(),
                        "link": url,
                        "source": name,
                    })

        return events

    def get_result(self):
        """Return events plus explicit provider health."""
        events = []
        successful = []
        failures = []

        for name, feed in self.FEEDS:
            try:
                provider_events = self._feed_events(name, feed)
                events.extend(provider_events)
                successful.append(name)
                self.providers[name] = "available"
            except Exception as ex:
                self.providers[name] = "failed"
                failures.append(f"{name}: {ex}")
                logger.warning("Calendar feed %s failed: %s", feed, ex)

        # Official sources are used when the primary feed is unavailable or empty.
        if not events:
            for name, url in self.OFFICIAL_SOURCES:
                try:
                    provider_events = self._official_events(name, url)
                    events.extend(provider_events)
                    successful.append(name)
                    self.providers[name] = "available"
                    if provider_events:
                        break
                except Exception as ex:
                    self.providers[name] = "failed"
                    failures.append(f"{name}: {ex}")
                    logger.warning("Official calendar source %s failed: %s", url, ex)

        unique = {}
        for event in events:
            key = (event.get("title", "").strip().lower(), event.get("published", ""))
            unique[key] = event
        events = list(unique.values())

        if events:
            self.status = "available"
        elif successful:
            self.status = "available_empty"
        else:
            self.status = "degraded"

        return {
            "events": events,
            "status": self.status,
            "providers": dict(self.providers),
            "errors": failures,
        }

    def get_events(self):
        """Backward-compatible event-only API."""
        return self.get_result()["events"]
