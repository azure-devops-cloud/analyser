from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.reasoner_service import ReasonerService


class ReasonerAgent(BaseAgent):
    """Explain deterministic decisions from the evidence ledger."""

    def run(self, context):
        try:
            service = ReasonerService()
            reasoning = [
                service.analyze(decision, context.evidence)
                for decision in context.decisions
            ]
            context.add_reasoning(reasoning)
            return AgentResult(
                agent="reasoner_agent",
                status="success",
                data={"reasoning": reasoning},
                count=len(reasoning),
            )
        except Exception as ex:
            return AgentResult(agent="reasoner_agent", status="failed", errors=[str(ex)])
