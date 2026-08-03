import feedparser
import requests


class RSSService:

    DEFAULT_ITEM_LIMIT = 20

    @staticmethod
    def get_feed(url, item_limit=None, timeout=20):
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "MarketMind-AI/0.2"},
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        articles = []
        limit = item_limit or RSSService.DEFAULT_ITEM_LIMIT

        for entry in feed.entries[:limit]:

            articles.append(
                {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": url,
                }
            )

        return articles
