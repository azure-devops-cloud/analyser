"""Aggregate data, event, and volatility risk into a reportable risk posture."""

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class RiskAgent(BaseAgent):
    """Assess market risk without creating trading instructions."""

    def run(self, context):
        try:
            reasons = []
            level = "low"
            max_volatility = max(
                (float(item.get("volatility", 0)) for item in context.market or []), default=0
            )
            if max_volatility > 40:
                level = "high"
                reasons.append("At least one asset has high annualized volatility.")
            elif max_volatility > 20:
                level = "medium"
                reasons.append("Market volatility is elevated.")

            if context.calendar:
                level = "high" if level == "medium" else level
                reasons.append("Scheduled economic events can increase event risk.")
            if (context.confidence or {}).get("score", 0) < 60:
                level = "high"
                reasons.append("Evidence confidence is below the safe operating threshold.")
            if not reasons:
                reasons.append("No material risk escalation was detected from available data.")

            data = {"level": level, "reasons": reasons, "max_volatility": max_volatility}
            context.add_risk(data)
            return AgentResult(agent="risk_agent", status="success", data=data, count=1)
        except Exception as ex:
            return AgentResult(agent="risk_agent", status="failed", errors=[str(ex)])
