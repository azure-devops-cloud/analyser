from dataclasses import dataclass, field
from typing import Iterable, List, Mapping, Sequence
from uuid import uuid4

from core.agent_registry import AgentRegistry
from models.agent_contracts import AgentTask


@dataclass(frozen=True)
class PlanStep:
    """A planned agent execution step with deterministic safety metadata."""

    agent: object
    phase: str
    critical: bool = False
    tags: Sequence[str] = field(default_factory=tuple)
    task: AgentTask | None = None


@dataclass(frozen=True)
class RunPlan:
    """Auditable plan selected before a manager run starts."""

    mode: str
    steps: Sequence[PlanStep]
    reason: str
    plan_id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def agent_names(self) -> List[str]:
        return [step.task.agent if step.task else step.agent.__class__.__name__ for step in self.steps]


class RunPlanner:
    """Build a deterministic control-plane plan from agent capabilities.

    The planner does not ask an LLM to decide safety boundaries. Intelligence
    remains inside agents, while phases, criticality, and task identity remain
    deterministic and auditable.
    """

    _PHASES = {
        "NewsCollectorAgent": "observe",
        "NewsIntelligenceAgent": "understand",
        "NewsSentimentAgent": "understand",
        "FactValidationAgent": "verify",
        "VerificationAgent": "verify",
        "DeduplicationAgent": "understand",
        "RankingAgent": "decide",
        "MarketAgent": "observe",
        "CalendarAgent": "observe",
        "TechnicalAnalysisAgent": "understand",
        "DecisionAgent": "decide",
        "ReasonerAgent": "reason",
        "ConfidenceAgent": "verify",
        "RiskAgent": "decide",
        "AlertAgent": "execute",
        "HistoryAgent": "learn",
        "MonitoringAgent": "observe",
        "SummaryAgent": "execute",
    }

    _CRITICAL = {"NewsCollectorAgent", "VerificationAgent", "DecisionAgent"}

    def plan(self, agents: Iterable, context: Mapping | object) -> RunPlan:
        """Return a validated, traceable plan without changing workflow order."""
        agents = tuple(agents)
        registry = AgentRegistry(agents)
        run_id = getattr(context, "run_id", uuid4().hex)
        steps = []

        for agent in agents:
            metadata = registry.metadata_for(agent)
            fallback_name = agent.__class__.__name__
            phase = metadata.phase or self._PHASES.get(fallback_name, "execute")
            critical = metadata.critical or fallback_name in self._CRITICAL
            task = AgentTask(
                agent=metadata.name,
                phase=phase,
                run_id=run_id,
                inputs={"capabilities": list(metadata.capabilities)},
            )
            steps.append(
                PlanStep(
                    agent=agent,
                    phase=phase,
                    critical=critical,
                    tags=(phase, *metadata.capabilities),
                    task=task,
                )
            )

        if not steps:
            return RunPlan(mode="empty", steps=(), reason="No agents were supplied")

        return RunPlan(
            mode="autonomous",
            steps=tuple(steps),
            reason="Capability-aware deterministic control policy selected the supplied dependency-safe workflow",
        )
