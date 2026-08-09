from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.verification_service import VerificationService


class VerificationAgent(BaseAgent):
    """Verify evidence quality and expose recovery guidance to the workflow."""

    def __init__(self, verification_service=None):
        self.service = verification_service or VerificationService()

    def run(self, context):
        try:
            result = self.service.verify(
                articles=context.news,
                evidence=context.evidence,
                intelligence=context.news_intelligence,
                source_trust=context.source_trust_map,
            )
            context.add_fact_validation(result)
            context.add_confidence({
                "verification": result["confidence_score"],
                "verification_status": result["status"],
            })
            return AgentResult(
                agent="verification_agent",
                status="success",
                data=result,
                count=result["evidence_count"],
            )
        except Exception as ex:
            return AgentResult(
                agent="verification_agent",
                status="failed",
                errors=[str(ex)],
            )
