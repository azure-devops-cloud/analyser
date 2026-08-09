from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from models.context import AgentContext
from agents.news_collector_agent import NewsCollectorAgent
from agents.news_intelligence_agent import NewsIntelligenceAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.fact_validation_agent import FactValidationAgent
from agents.verification_agent import VerificationAgent
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
from core.agent_orchestrator import AgentOrchestrator, RecoveryPolicy
from core.execution_graph import ExecutionGraph
from models.domain import AgentStatus, ExecutionMetric
from services.logger import get_logger
from services.metrics_service import MetricsService

logger = get_logger(__name__)


class ManagerAgent:
    """Top-level workflow agent coordinating the autonomous agent fleet."""

    def __init__(self, orchestrator=None):
        self.context = AgentContext()
        self.run_id = uuid4().hex
        self.agents = [
            NewsCollectorAgent(),
            NewsIntelligenceAgent(),
            NewsSentimentAgent(),
            FactValidationAgent(),
            VerificationAgent(),
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
        self.orchestrator = orchestrator or AgentOrchestrator(
            RecoveryPolicy(max_retries=1, backoff_seconds=0.25)
        )

    def run(self):
        metrics = MetricsService()
        started_state = {}

        def on_start(agent):
            node_name = agent.__class__.__name__
            started_state[node_name] = (
                datetime.now(timezone.utc),
                perf_counter(),
            )
            self.execution_graph.mark_running(node_name)

        def on_result(result, agent):
            node_name = agent.__class__.__name__
            started_at, started = started_state[node_name]
            duration_ms = (perf_counter() - started) * 1000

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
                    metadata={
                        "graph_node": node_name,
                        "orchestration": "autonomous",
                    },
                )
            except Exception:
                logger.exception("Unable to persist metric for %s", result.agent)

        try:
            results = self.orchestrator.execute(
                self.agents,
                self.context,
                on_start=on_start,
                on_result=on_result,
            )
        finally:
            metrics.close()

        self.context.add_execution(
            {
                "run_id": self.run_id,
                "graph": self.execution_graph.snapshot(),
                "orchestration": {
                    "mode": "autonomous",
                    "recovery": {
                        "max_retries": self.orchestrator.recovery_policy.max_retries,
                        "backoff_seconds": self.orchestrator.recovery_policy.backoff_seconds,
                    },
                },
            }
        )
        return results, self.context
