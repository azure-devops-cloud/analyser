from models.context import AgentContext
from agents.news_collector_agent import NewsCollectorAgent
from agents.deduplication_agent import DeduplicationAgent
from agents.ranking_agent import RankingAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent
from agents.alert_agent import AlertAgent
from agents.history_agent import HistoryAgent
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
            FactValidationAgent(),
            DeduplicationAgent(),
            RankingAgent(),
            MarketAgent(),
            CalendarAgent(),
            DecisionAgent(),
            AlertAgent(),
            HistoryAgent(),
            MonitoringAgent(),
            SummaryAgent()
        ]
    def run(self):
        results = []
        for agent in self.agents:
            result = agent.run(self.context)
            results.append(result)
            if result.status != "success":
                self.context.add_error(
                    f"{result.agent}: {', '.join(result.errors) or 'unknown error'}"
                )
        return results, self.context
