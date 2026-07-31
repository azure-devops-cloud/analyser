from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from config.rss_feeds import RSS_FEEDS
from services.rss_service import RSSService


class NewsAgent(BaseAgent):

    def run(self):

        articles = []

        try:

            for category, feeds in RSS_FEEDS.items():

                for feed in feeds:

                    results = RSSService.get_feed(feed)

                    for item in results:

                        item["category"] = category

                        articles.append(item)


            return AgentResult(
                agent="news_agent",
                status="success",
                data=articles,
                count=len(articles)
            )


        except Exception as error:

            return AgentResult(
                agent="news_agent",
                status="failed",
                errors=[str(error)]
            )
