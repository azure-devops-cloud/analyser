from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.reasoner_service import ReasonerService


class ReasonerAgent(BaseAgent):
    """Explain deterministic decisions from the evidence ledger."""

    def run(self, context):
        try:
            service = ReasonerService()
            decisions = context.get("decisions", []) if isinstance(context, dict) else context.decisions
            evidence = context.get("evidence", []) if isinstance(context, dict) else context.evidence
            reasoning = [service.analyze(decision, evidence) for decision in decisions]

            if isinstance(context, dict):
                context["reasoning"] = reasoning
            else:
                context.add_reasoning(reasoning)

            return AgentResult(
                agent="reasoner_agent",
                status="success",
                data=reasoning,
                count=len(reasoning),
            )
        except Exception as ex:
            return AgentResult(
                agent="reasoner_agent",
                status="failed",
                errors=[str(ex)],
            )
