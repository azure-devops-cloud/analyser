from agents.base_agent import BaseAgent

from models.agent_result import AgentResult

from services.sentiment_service import SentimentService


class NewsSentimentAgent(BaseAgent):

    def run(self, context):

        service = SentimentService()

        analysis = []

        positive = 0
        negative = 0
        neutral = 0

        for article in context.news:

            result = service.analyze(

                article["title"]

            )

            article["sentiment"] = result["sentiment"]

            article["sentiment_score"] = result["score"]

            analysis.append(article)

            if result["sentiment"]=="POSITIVE":

                positive +=1

            elif result["sentiment"]=="NEGATIVE":

                negative +=1

            else:

                neutral +=1

        context.news = analysis

        return AgentResult(

            agent="news_sentiment_agent",

            status="success",

            count=len(analysis),

            data={

                "positive":positive,

                "negative":negative,

                "neutral":neutral

            }

        )
