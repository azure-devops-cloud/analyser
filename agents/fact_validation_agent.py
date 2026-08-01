from collections import Counter

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class FactValidationAgent(BaseAgent):

    def run(self, context):
        try:
            topics = Counter()
            for article in context.news or []:
                title = article.get("title", "")
                if title:
                    topics[title.strip()] += 1

            evidence_count = sum(count for count in topics.values() if count > 1)
            confidence_score = min(100, max(40, evidence_count * 20))

            return AgentResult(
                agent="fact_validation_agent",
                status="success",
                data={
                    "evidence_count": evidence_count,
                    "confidence_score": confidence_score,
                    "verification_status": "validated" if evidence_count > 0 else "needs_more_sources",
                },
                count=evidence_count
            )
        except Exception as ex:
            return AgentResult(
                agent="fact_validation_agent",
                status="failed",
                errors=[str(ex)]
            )
