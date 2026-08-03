from collections import OrderedDict
import re

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class DeduplicationAgent(BaseAgent):

    @staticmethod
    def _normalize(text):
        if not text:
            return ""
        cleaned = re.sub(r"[^a-z0-9\s]", " ", str(text).lower())
        return " ".join(cleaned.split())

    @staticmethod
    def _article_quality(article):
        return (
            int(article.get("source_priority", 1)) * 10
            + int(article.get("impact_score", 0))
            + int(article.get("sentiment_score", 0)) * 5
        )

    @staticmethod
    def _similarity(first, second):
        first_tokens = set(DeduplicationAgent._normalize(first).split())
        second_tokens = set(DeduplicationAgent._normalize(second).split())
        if not first_tokens and not second_tokens:
            return 1.0
        if not first_tokens or not second_tokens:
            return 0.0
        overlap = len(first_tokens & second_tokens)
        union = len(first_tokens | second_tokens)
        return overlap / union if union else 0.0

    def run(self, context):
        try:
            original_count = len(context.news or [])
            deduped = OrderedDict()
            title_clusters = OrderedDict()

            for article in context.news or []:
                title = article.get("title", "")
                title_key = self._normalize(title)
                if not title_key:
                    title_key = article.get("link") or article.get("url") or str(article)

                if title_key in title_clusters:
                    current = title_clusters[title_key]
                    if self._article_quality(article) > self._article_quality(current):
                        title_clusters[title_key] = article
                    continue

                title_clusters[title_key] = article

            for article in title_clusters.values():
                link = article.get("link") or article.get("url")
                if link:
                    deduped[link] = article
                else:
                    deduped[article.get("title", "")] = article

            final_articles = list(deduped.values())
            context.add_news(final_articles)

            return AgentResult(
                agent="deduplication_agent",
                status="success",
                data={
                    "articles": final_articles,
                    "removed_duplicates": max(original_count - len(final_articles), 0)
                },
                count=len(final_articles)
            )
        except Exception as ex:
            return AgentResult(
                agent="deduplication_agent",
                status="failed",
                errors=[str(ex)]
            )
