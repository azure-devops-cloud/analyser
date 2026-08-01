from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.market_data_service import MarketService


class MarketAgent(BaseAgent):


    def run(self):

        try:

            service = MarketDataService()

            data = service.get_market_data()


            return AgentResult(

                agent="market_agent",

                status="success",

                data=data,

                count=len(data)

            )


        except Exception as error:


            return AgentResult(

                agent="market_agent",

                status="failed",

                errors=[str(error)]

            )
