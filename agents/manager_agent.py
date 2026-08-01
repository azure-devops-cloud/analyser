from models.context import AgentContext
from agents.news_agent import NewsAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent
from agents.calendar_agent import CalendarAgent

class ManagerAgent:
    def __init__(self):
        self.context = AgentContext()
        self.agents = [
            NewsAgent(),
            MarketAgent(),
            DecisionAgent(),
            CalendarAgent()
        ]
    def run(self):
        results = []
        for agent in self.agents:
            result = agent.run(self.context)
            results.append(result)
        return results, self.context
