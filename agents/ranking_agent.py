from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class RankingAgent(BaseAgent):

    def run(self, context):
        try:
            ranked = []

            for article in context.news or []:
                sentiment_score = article.get("sentiment_score", 0)
                impact_score = article.get("impact_score", 0)
                base_score = max(0, min(100, (sentiment_score * 12) + impact_score))

                article["importance_score"] = base_score
                ranked.append(article)

            context.add_news(ranked)

            top_story = max(ranked, key=lambda item: item.get("importance_score", 0), default=None)

            return AgentResult(
                agent="ranking_agent",
                status="success",
                data={
                    "articles": ranked,
                    "top_story": top_story,
                    "top_score": top_story.get("importance_score", 0) if top_story else 0,
                },
                count=len(ranked)
            )
        except Exception as ex:
            return AgentResult(
                agent="ranking_agent",
                status="failed",
                errors=[str(ex)]
            )
