from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.market_data_service import MarketService
from services.market_history_service import MarketHistoryService


class MarketAgent(BaseAgent):

    def run(self, context):

        try:

            service = MarketService()

            data = service.get_market_data()
            history = MarketHistoryService()
            try:
                data = history.record(data)
            finally:
                history.close()
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
