from models.context import AgentContext
from agents.news_collector_agent import NewsCollectorAgent
from agents.deduplication_agent import DeduplicationAgent
from agents.ranking_agent import RankingAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent
from agents.calendar_agent import CalendarAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.fact_validation_agent import FactValidationAgent
from agents.monitoring_agent import MonitoringAgent
from agents.summary_agent import SummaryAgent

class ManagerAgent:
    def __init__(self):
        self.context = AgentContext()
        self.agents = [
            NewsCollectorAgent(),
            NewsSentimentAgent(),
            DeduplicationAgent(),
            RankingAgent(),
            MarketAgent(),
            CalendarAgent(),
            DecisionAgent(),
            FactValidationAgent(),
            MonitoringAgent(),
            SummaryAgent()
        ]
    def run(self):
        results = []
        for agent in self.agents:
            result = agent.run(self.context)
            results.append(result)
        return results, self.context
