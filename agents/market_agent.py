from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.market_data_service import MarketService


class MarketAgent(BaseAgent):

    def run(self, context):

        try:

            service = MarketService()

            data = service.get_market_data()
            context.add_market(data)

            return AgentResult(
                agent="market_agent",
                status="success",
                data=data,
                count=len(data)
            )

        except Exception as ex:

            return AgentResult(
                agent="market_agent",
                status="failed",
                errors=[str(ex)]
            )
