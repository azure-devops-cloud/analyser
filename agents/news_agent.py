from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from config.rss_feeds import RSS_FEEDS, CATEGORY_ARTICLE_CAP

from services.rss_service import RSSService
from services.news_storage_service import NewsStorageService
from services.classifier_service import ClassifierService
from services.news_analysis_service import NewsAnalysisService
from services.logger import get_logger


logger = get_logger(__name__)


class NewsAgent(BaseAgent):


    def run(self, context):

        articles = []


        try:

            classifier = ClassifierService()

            for category, feeds in RSS_FEEDS.items():
                category_articles = 0

                for feed_data in feeds:
                    if isinstance(feed_data, tuple):
                        feed, priority = feed_data
                    else:
                        feed = feed_data
                        priority = 1

                    if category_articles >= CATEGORY_ARTICLE_CAP:
                        break

                    try:
                        try:
                            results = RSSService.get_feed(feed, item_limit=max(priority, 1) * 5)
                        except TypeError:
                            results = RSSService.get_feed(feed)

                        for item in results:
                            if category_articles >= CATEGORY_ARTICLE_CAP:
                                break

                            item["source_category"] = category
                            item = classifier.classify(item)
                            articles.append(item)
                            category_articles += 1

                    except Exception as feed_error:

                        logger.warning(
                            "Feed %s failed: %s",
                            feed,
                            str(feed_error)
                        )

                        continue

                    except Exception as feed_error:

                        logger.warning(
                            "Feed %s failed: %s",
                            feed,
                            str(feed_error)
                        )

                        continue


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

            context.add_news(articles)

            return AgentResult(

                agent="news_agent",
            
                status="success",
            
                data={
            
                    "articles": articles,
            
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
