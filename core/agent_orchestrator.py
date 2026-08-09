from dataclasses import dataclass
from re import search, sub
from time import sleep
from typing import Callable, Iterable, Optional

from models.agent_result import AgentResult
from services.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class RecoveryPolicy:
    """Bounded recovery policy for autonomous agent execution."""

    max_retries: int = 1
    backoff_seconds: float = 0.25
    retryable_patterns: tuple[str, ...] = (
        "temporary",
        "timeout",
        "timed out",
        "unavailable",
        "rate limit",
        "429",
        "502",
        "503",
        "504",
        "connection",
    )
    stop_on_critical_failure: bool = False


class AgentOrchestrator:
    """Execute planned agents with bounded recovery and fail-safe continuation."""

    def __init__(self, recovery_policy: Optional[RecoveryPolicy] = None):
        self.recovery_policy = recovery_policy or RecoveryPolicy()

    def execute(
        self,
        agents: Iterable,
        context,
        on_start: Optional[Callable[[object], None]] = None,
        on_result: Optional[Callable[[AgentResult, object], None]] = None,
        plan=None,
    ) -> list[AgentResult]:
        results = []
        steps = list(plan.steps) if plan is not None else [
            type("ExecutionStep", (), {"agent": agent, "critical": False})
            for agent in agents
        ]

        for step in steps:
            agent = step.agent
            if on_start:
                on_start(agent)
            result = self._execute_agent(agent, context)
            results.append(result)
            if on_result:
                on_result(result, agent)

            if (
                result.status == "failed"
                and getattr(step, "critical", False)
                and self.recovery_policy.stop_on_critical_failure
            ):
                logger.error(
                    "Stopping autonomous plan after critical agent failure: %s",
                    result.agent,
                )
                break
        return results

    @staticmethod
    def _agent_id(agent) -> str:
        """Return a stable public identifier for an agent result."""
        explicit = getattr(agent, "agent_name", None) or getattr(agent, "name", None)
        if explicit:
            return explicit
        class_name = agent.__class__.__name__
        return sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()

    def _is_retryable(self, message: str) -> bool:
        normalized = (message or "").lower()
        return any(search(pattern, normalized) for pattern in self.recovery_policy.retryable_patterns)

    def _execute_agent(self, agent, context) -> AgentResult:
        attempts = self.recovery_policy.max_retries + 1
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                result = agent.run(context)
                if not isinstance(result, AgentResult):
                    return AgentResult(
                        agent=self._agent_id(agent),
                        status="failed",
                        errors=["Agent returned an invalid result type"],
                    )
                if result.status == "success":
                    return result
                last_error = "; ".join(result.errors) or "agent reported failure"
            except Exception as exc:
                last_error = str(exc)
                logger.exception(
                    "Agent %s failed on attempt %s/%s",
                    agent.__class__.__name__,
                    attempt,
                    attempts,
                )

            if attempt >= attempts or not self._is_retryable(last_error):
                break

            if self.recovery_policy.backoff_seconds > 0:
                sleep(self.recovery_policy.backoff_seconds * attempt)

        return AgentResult(
            agent=self._agent_id(agent),
            status="failed",
            errors=[last_error or "agent execution failed after recovery attempts"],
        )
