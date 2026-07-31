from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from config.rss_feeds import RSS_FEEDS

from services.rss_service import RSSService
from services.news_storage_service import NewsStorageService
from services.classifier_service import ClassifierService
from services.news_analysis_service import NewsAnalysisService
from services.logger import get_logger


logger = get_logger(__name__)


class NewsAgent(BaseAgent):


    def run(self):

        articles = []


        try:

            classifier = ClassifierService()


            for category, feeds in RSS_FEEDS.items():

                for feed in feeds:


                    results = RSSService.get_feed(feed)


                    for item in results:

                        item["source_category"] = category


                        item = classifier.classify(
                            item
                        )


                        articles.append(item)



            logger.info(
                f"RSS Articles Checked: {len(articles)}"
            )


            storage = NewsStorageService()


            new_articles = storage.save_news(
                articles
            )


            storage.close()



            analyzer = NewsAnalysisService()


            analysis = analyzer.analyze(
                articles
            )



            return AgentResult(

                agent="news_agent",

                status="success",

                data={

                    "new_articles": new_articles,

                    "total_checked": len(articles),

                    "analysis": analysis

                },

                count=len(new_articles)

            )


        except Exception as error:


            logger.error(
                str(error)
            )


            return AgentResult(

                agent="news_agent",

                status="failed",

                errors=[str(error)]

            )
