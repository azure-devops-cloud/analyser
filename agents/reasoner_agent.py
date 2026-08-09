from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.reasoner_service import ReasonerService
from services.llm_reasoner_service import LLMReasonerService


class ReasonerAgent(BaseAgent):
    """Explain deterministic decisions and optionally synthesize them with an LLM."""

    def __init__(self, llm_client=None):
        self.reasoner = ReasonerService()
        self.llm_reasoner = LLMReasonerService(client=llm_client)

    def run(self, context):
        try:
            decisions = context.get("decisions", []) if isinstance(context, dict) else context.decisions
            evidence = context.get("evidence", []) if isinstance(context, dict) else context.evidence
            reasoning = [self.reasoner.analyze(decision, evidence) for decision in decisions]
            for packet in reasoning:
                packet["explanation"] = self.llm_reasoner.synthesize(packet)
            if isinstance(context, dict):
                context["reasoning"] = reasoning
            else:
                context.add_reasoning(reasoning)
            return AgentResult(agent="reasoner_agent", status="success", data=reasoning, count=len(reasoning))
        except Exception as ex:
            return AgentResult(agent="reasoner_agent", status="failed", errors=[str(ex)])
