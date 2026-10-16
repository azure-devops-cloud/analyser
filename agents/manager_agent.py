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
from config.settings import SETTINGS
from core.agent_orchestrator import AgentOrchestrator, RecoveryPolicy
from core.agent_registry import AgentRegistry
from core.execution_graph import ExecutionGraph
from core.health_monitor import HealthMonitor
from core.memory_store import MemoryStore
from core.run_planner import RunPlanner
from core.validation_engine import ValidationEngine
from models.domain import AgentStatus, ExecutionMetric
from services.logger import get_logger
from services.metrics_service import MetricsService

logger = get_logger(__name__)


class ManagerAgent:
    """Supervisor/control-plane agent coordinating the autonomous intelligence fleet."""

    def __init__(self, orchestrator=None, planner=None, memory_store=None):
        self.run_id = uuid4().hex
        self.context = AgentContext(run_id=self.run_id)
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
        self.registry = AgentRegistry(self.agents)
        self.execution_graph = ExecutionGraph()
        for metadata in self.registry.metadata():
            self.execution_graph.add_node(
                metadata.name,
                metadata={"phase": metadata.phase, "capabilities": list(metadata.capabilities)},
            )
        self.planner = planner or RunPlanner()
        self.orchestrator = orchestrator or AgentOrchestrator(
            RecoveryPolicy(
                max_retries=SETTINGS.agent_max_retries,
                backoff_seconds=SETTINGS.agent_backoff_seconds,
                stop_on_critical_failure=SETTINGS.agent_stop_on_critical_failure,
            )
        )
        self.memory = memory_store or MemoryStore(SETTINGS.database_path)
        self.validator = ValidationEngine()
        self.health = HealthMonitor()

    def run(self):
        metrics = MetricsService()
        started_state = {}
        plan = self.planner.plan(self.agents, self.context)
        self.context.set_metadata("plan_id", plan.plan_id)
        self.context.set_metadata(
            "agent_capabilities",
            [metadata.as_dict() for metadata in self.registry.metadata()],
        )

        def on_start(agent):
            node_name = self.registry.metadata_for(agent).name
            started_state[node_name] = (datetime.now(timezone.utc), perf_counter())
            self.execution_graph.mark_running(node_name)

        def on_result(result, agent):
            node_name = self.registry.metadata_for(agent).name
            started_at, started = started_state[node_name]
            duration_ms = (perf_counter() - started) * 1000

            if result.status == "success":
                self.execution_graph.mark_success(node_name)
            else:
                error = ", ".join(result.errors) or "unknown error"
                self.execution_graph.mark_failed(node_name, error)
                self.context.add_error(f"{result.agent}: {error}")

            try:
                step = next(step for step in plan.steps if step.agent is agent)
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
                        "plan_id": plan.plan_id,
                        "plan_phase": step.phase,
                        "task_id": result.task_id,
                        "attempts": result.attempts,
                        "retryable": result.retryable,
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
                plan=plan,
            )
        finally:
            metrics.close()

        validation = self.validator.validate(self.context.decisions, self.context.evidence)
        self.context.set_metadata("validation", validation.as_dict())
        self.context.set_metadata(
            "health",
            [signal.as_dict() for signal in self.health.assess(results, self.context)],
        )
        self.context.set_metadata("degraded", not validation.passed or bool(self.context.errors))

        # Selective episodic memory: keep compact outcomes, not raw external content.
        self.memory.put(
            f"run:{self.run_id}",
            "episodic_run",
            {
                "run_id": self.run_id,
                "plan_id": plan.plan_id,
                "validation": validation.as_dict(),
                "errors": list(self.context.errors),
                "decision_count": len(self.context.decisions),
                "evidence_count": len(self.context.evidence),
            },
            ttl_days=90,
        )
        for decision in self.context.decisions:
            if isinstance(decision, dict):
                name = str(decision.get("name") or decision.get("asset") or "unknown").lower()
                self.memory.put(
                    f"decision:{name}:{self.run_id}",
                    "decision_history",
                    {
                        "run_id": self.run_id,
                        "asset": name,
                        "bias": decision.get("bias"),
                        "score": decision.get("score"),
                        "confidence": decision.get("confidence"),
                    },
                    ttl_days=365,
                )

        self.context.add_execution(
            {
                "run_id": self.run_id,
                "graph": self.execution_graph.snapshot(),
                "context": self.context.snapshot(),
                "validation": validation.as_dict(),
                "health": self.context.metadata["health"],
                "orchestration": {
                    "mode": plan.mode,
                    "plan_id": plan.plan_id,
                    "plan_reason": plan.reason,
                    "planned_agents": plan.agent_names,
                    "recovery": {
                        "max_retries": self.orchestrator.recovery_policy.max_retries,
                        "backoff_seconds": self.orchestrator.recovery_policy.backoff_seconds,
                        "retryable_patterns": list(self.orchestrator.recovery_policy.retryable_patterns),
                        "stop_on_critical_failure": self.orchestrator.recovery_policy.stop_on_critical_failure,
                    },
                    "events": [event.as_dict() for event in self.context.events],
                },
            }
        )
        return results, self.context
