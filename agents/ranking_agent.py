from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.source_trust_service import SourceTrustService


class RankingAgent(BaseAgent):

    @staticmethod
    def _importance_score(article, trust_map):
        sentiment_score = int(article.get("sentiment_score", 0))
        impact_score = int(article.get("impact_score", 0))
        source_priority = int(article.get("source_priority", 1))
        confidence = int(article.get("confidence_score", 0))
        source_key = str(article.get("link") or article.get("url") or article.get("source") or article.get("title") or "")
        trust_score = int(trust_map.get(source_key, 60)) if trust_map else 60

        base_score = (sentiment_score * 12) + impact_score + (source_priority * 5) + confidence + trust_score
        return max(0, base_score)

    def run(self, context):
        try:
            trust_map = context.source_trust_map or SourceTrustService().as_dict()
            ranked = []

            for article in context.news or []:
                article["importance_score"] = self._importance_score(article, trust_map)
                ranked.append(article)

            context.add_news(ranked)
            context.add_source_trust_map(trust_map)

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
