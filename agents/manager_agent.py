from models.context import AgentContext
from agents.news_collector_agent import NewsCollectorAgent
from agents.news_intelligence_agent import NewsIntelligenceAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.fact_validation_agent import FactValidationAgent
from agents.deduplication_agent import DeduplicationAgent
from agents.ranking_agent import RankingAgent
from agents.market_agent import MarketAgent
from agents.decision_agent import DecisionAgent
from agents.reasoner_agent import ReasonerAgent
from agents.alert_agent import AlertAgent
from agents.history_agent import HistoryAgent
from agents.calendar_agent import CalendarAgent
from agents.monitoring_agent import MonitoringAgent
from agents.summary_agent import SummaryAgent
from agents.technical_analysis_agent import TechnicalAnalysisAgent
from agents.confidence_agent import ConfidenceAgent
from agents.risk_agent import RiskAgent
from core.execution_graph import ExecutionGraph
from models.domain import AgentStatus, ExecutionMetric
from services.logger import get_logger
from services.metrics_service import MetricsService
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

logger = get_logger(__name__)


class ManagerAgent:
    def __init__(self):
        self.context = AgentContext()
        self.run_id = uuid4().hex
        self.agents = [
            NewsCollectorAgent(),
            NewsIntelligenceAgent(),
            NewsSentimentAgent(),
            FactValidationAgent(),
            DeduplicationAgent(),
            RankingAgent(),
            MarketAgent(),
            CalendarAgent(),
            TechnicalAnalysisAgent(),
            DecisionAgent(),
            ReasonerAgent(),
            ConfidenceAgent(),
            RiskAgent(),
            AlertAgent(),
            HistoryAgent(),
            MonitoringAgent(),
            SummaryAgent(),
        ]
        self.execution_graph = ExecutionGraph()
        for agent in self.agents:
            self.execution_graph.add_node(agent.__class__.__name__)

    def run(self):
        results = []
        metrics = MetricsService()
        try:
            for agent in self.agents:
                node_name = agent.__class__.__name__
                started_at = datetime.now(timezone.utc)
                started = perf_counter()
                self.execution_graph.mark_running(node_name)
                result = agent.run(self.context)
                duration_ms = (perf_counter() - started) * 1000
                results.append(result)
                if result.status == "success":
                    self.execution_graph.mark_success(node_name)
                else:
                    error = ", ".join(result.errors) or "unknown error"
                    self.execution_graph.mark_failed(node_name, error)
                    self.context.add_error(f"{result.agent}: {error}")
                try:
                    metrics.record(
                        ExecutionMetric(
                            run_id=self.run_id,
                            agent=result.agent,
                            status=AgentStatus(result.status),
                            started_at=started_at,
                            duration_ms=round(duration_ms, 3),
                            item_count=result.count,
                            error_count=len(result.errors),
                        ),
                        metadata={"graph_node": node_name},
                    )
                except Exception:
                    logger.exception("Unable to persist metric for %s", result.agent)
        finally:
            metrics.close()
        self.context.add_execution({"run_id": self.run_id, "graph": self.execution_graph.snapshot()})
        return results, self.context
