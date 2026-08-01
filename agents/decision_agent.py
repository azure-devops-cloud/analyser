from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.decision_service import DecisionService


class DecisionAgent(BaseAgent):

    def run(self, context):

        try:

            market_data = context.market

            decision = DecisionService()

            analysis = []

            for item in market_data:

                analysis.append(
                    decision.analyze(item)
                )

            context.add_decisions(analysis)

            return AgentResult(
                agent="decision_agent",
                status="success",
                data=analysis,
                count=len(analysis)
            )

        except Exception as ex:

            return AgentResult(
                agent="decision_agent",
                status="failed",
                errors=[str(ex)]
            )
