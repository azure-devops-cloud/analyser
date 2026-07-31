from agents.news_agent import NewsAgent
from agents.market_agent import MarketAgent



class ManagerAgent:


    def __init__(self):

        self.agents = [

            NewsAgent(),

            MarketAgent()

        ]


    def run(self):

        results = []


        for agent in self.agents:

            results.append(
                agent.run()
            )


        return results
