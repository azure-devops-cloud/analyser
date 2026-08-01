import feedparser


class RSSService:

    DEFAULT_ITEM_LIMIT = 20

    @staticmethod
    def get_feed(url, item_limit=None):

        feed = feedparser.parse(url)

        articles = []
        limit = item_limit or RSSService.DEFAULT_ITEM_LIMIT

        for entry in feed.entries[:limit]:

            articles.append(
                {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "")
                }
            )

        return articles
