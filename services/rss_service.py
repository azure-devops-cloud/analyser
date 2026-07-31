import feedparser


class RSSService:

    @staticmethod
    def get_feed(url):

        feed = feedparser.parse(url)

        articles = []

        for entry in feed.entries:

            articles.append(
                {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "")
                }
            )

        return articles
