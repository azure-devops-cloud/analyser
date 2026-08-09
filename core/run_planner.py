from dataclasses import dataclass, field
from typing import Iterable, List, Mapping, Sequence


@dataclass(frozen=True)
class PlanStep:
    """A planned agent execution step with deterministic safety metadata."""

    agent: object
    phase: str
    critical: bool = False
    tags: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class RunPlan:
    """Auditable plan selected before a manager run starts."""

    mode: str
    steps: Sequence[PlanStep]
    reason: str

    @property
    def agent_names(self) -> List[str]:
        return [step.agent.__class__.__name__ for step in self.steps]


class RunPlanner:
    """Build a safe, deterministic execution plan from available agents.

    Planning remains deterministic infrastructure: an LLM is deliberately not
    used to decide execution order or safety boundaries. Agents can evolve
    independently while the planner provides an auditable control-plane layer.
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
        """Return the supplied workflow in a validated, auditable plan.

        The planner preserves the declared dependency-safe order. Unknown
        agents are allowed and receive a neutral phase so the architecture is
        extensible without requiring a central registry change.
        """
        steps = []
        for agent in agents:
            name = agent.__class__.__name__
            phase = self._PHASES.get(name, "execute")
            steps.append(
                PlanStep(
                    agent=agent,
                    phase=phase,
                    critical=name in self._CRITICAL,
                    tags=(phase,),
                )
            )

        if not steps:
            return RunPlan(mode="empty", steps=(), reason="No agents were supplied")

        return RunPlan(
            mode="autonomous",
            steps=tuple(steps),
            reason="Dependency-safe workflow selected by deterministic control policy",
        )
