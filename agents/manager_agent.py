from models.context import AgentContext
from agents.news_agent import NewsAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent
from agents.calendar_agent import CalendarAgent
from agents.news_sentiment_agent import NewsSentimentAgent

class ManagerAgent:
    def __init__(self):
        self.context = AgentContext()
        self.agents = [
            NewsAgent(),
            NewsSentimentAgent(),
            MarketAgent(),
            CalendarAgent(),
            DecisionAgent()    
        ]
    def run(self):
        results = []
        for agent in self.agents:
            result = agent.run(self.context)
            results.append(result)
        return results, self.context
