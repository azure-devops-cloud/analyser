from collections import OrderedDict

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class DeduplicationAgent(BaseAgent):

    def run(self, context):
        try:
            deduped = OrderedDict()

            for article in context.news or []:
                unique_key = article.get("link") or article.get("title") or article.get("url")
                if unique_key:
                    deduped[unique_key] = article

            final_articles = list(deduped.values())
            context.add_news(final_articles)

            return AgentResult(
                agent="deduplication_agent",
                status="success",
                data={
                    "articles": final_articles,
                    "removed_duplicates": max(len(context.news or []) - len(final_articles), 0)
                },
                count=len(final_articles)
            )
        except Exception as ex:
            return AgentResult(
                agent="deduplication_agent",
                status="failed",
                errors=[str(ex)]
            )
