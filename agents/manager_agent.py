from agents.news_agent import NewsAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent


class ManagerAgent:

    def __init__(self):

        self.agents = [

            NewsAgent(),

            MarketAgent(),

            DecisionAgent()

        ]

    def run(self):

        results = []

        for agent in self.agents:

            results.append(

                agent.run()

            )

        return results
