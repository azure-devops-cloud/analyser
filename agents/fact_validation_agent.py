from urllib.parse import urlparse

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class FactValidationAgent(BaseAgent):

    def run(self, context):
        try:
            topics = {}
            for article in context.news or []:
                title = " ".join(article.get("title", "").lower().split())
                if title:
                    source = article.get("source") or article.get("link", "")
                    source_id = urlparse(source).netloc or source
                    topics.setdefault(title, set()).add(source_id)

            corroborated_topics = [sources for sources in topics.values() if len(sources) > 1]
            evidence_count = sum(len(sources) for sources in corroborated_topics)
            confidence_score = min(100, 40 + (len(corroborated_topics) * 30))
            result_data = {
                "evidence_count": evidence_count,
                "confidence_score": confidence_score,
                "verification_status": "validated" if corroborated_topics else "needs_more_sources",
            }

            context.add_fact_validation(result_data)

            return AgentResult(
                agent="fact_validation_agent",
                status="success",
                data=result_data,
                count=evidence_count
            )
        except Exception as ex:
            return AgentResult(
                agent="fact_validation_agent",
                status="failed",
                errors=[str(ex)]
            )
