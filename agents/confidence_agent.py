"""Score evidence completeness and agreement for recommendations."""

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class ConfidenceAgent(BaseAgent):
    """Produce transparent confidence scores from available pipeline evidence."""

    def run(self, context):
        try:
            fact_validation = context.fact_validation or {}
            score = 20
            reasons = ["Base model confidence applied."]
            if context.market:
                score += 25
                reasons.append("Live market data is available.")
            if context.news:
                score += 15
                reasons.append("Relevant news was collected.")
            if fact_validation.get("verification_status") == "validated":
                score += 20
                reasons.append("News evidence was corroborated across sources.")
            if context.technical_analysis:
                score += 10
                reasons.append("Technical analysis is available.")
            if context.calendar:
                score += 5
                reasons.append("Economic calendar was considered.")

            score = min(score, 100)
            data = {
                "score": score,
                "level": "high" if score >= 80 else "medium" if score >= 60 else "low",
                "reasons": reasons,
            }
            context.add_confidence(data)
            return AgentResult(
                agent="confidence_agent", status="success", data=data, count=1
            )
        except Exception as ex:
            return AgentResult(agent="confidence_agent", status="failed", errors=[str(ex)])
