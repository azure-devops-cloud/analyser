from config.rss_feeds import RSS_FEEDS
from services.rss_service import RSSService

class NewsAgent:

    def run(self):

        news = []

        for category, feeds in RSS_FEEDS.items():

            for feed in feeds:

                articles = RSSService.get_feed(feed)

                for article in articles:

                    article["category"] = category

                    news.append(article)

        return news
