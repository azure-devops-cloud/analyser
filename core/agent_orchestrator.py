from dataclasses import dataclass
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


class AgentOrchestrator:
    """Execute agents with bounded recovery and fail-safe continuation.

    The orchestrator owns execution policy while individual agents own domain
    behavior. A failed agent never causes an unrelated downstream agent to be
    silently reported as successful; its failure is returned as an AgentResult
    and the shared context remains available for degraded-mode execution.
    """

    def __init__(self, recovery_policy: Optional[RecoveryPolicy] = None):
        self.recovery_policy = recovery_policy or RecoveryPolicy()

    def execute(
        self,
        agents: Iterable,
        context,
        on_result: Optional[Callable[[AgentResult, object], None]] = None,
    ) -> list[AgentResult]:
        results = []
        for agent in agents:
            result = self._execute_agent(agent, context)
            results.append(result)
            if on_result:
                on_result(result, agent)
        return results

    def _execute_agent(self, agent, context) -> AgentResult:
        attempts = self.recovery_policy.max_retries + 1
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                result = agent.run(context)
                if not isinstance(result, AgentResult):
                    return AgentResult(
                        agent=getattr(agent, "name", agent.__class__.__name__),
                        status="failed",
                        errors=["Agent returned an invalid result type"],
                    )
                if result.status == "success":
                    return result
                last_error = "; ".join(result.errors) or "agent reported failure"
            except Exception as exc:  # defensive boundary around third-party/domain agents
                last_error = str(exc)
                logger.exception(
                    "Agent %s failed on attempt %s/%s",
                    agent.__class__.__name__,
                    attempt,
                    attempts,
                )

            if attempt < attempts and self.recovery_policy.backoff_seconds > 0:
                sleep(self.recovery_policy.backoff_seconds * attempt)

        return AgentResult(
            agent=getattr(agent, "name", agent.__class__.__name__),
            status="failed",
            errors=[last_error or "agent execution failed after recovery attempts"],
        )
