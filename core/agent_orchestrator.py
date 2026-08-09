from dataclasses import dataclass
from re import search, sub
from time import perf_counter, sleep
from typing import Callable, Iterable, Optional
from uuid import uuid4

from models.agent_contracts import RecoveryDecision
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

    def __post_init__(self):
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.backoff_seconds < 0:
            raise ValueError("backoff_seconds must be >= 0")


class AgentOrchestrator:
    """Execute agents with bounded recovery, audit events, and fail-safe continuation."""

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
            type("ExecutionStep", (), {"agent": agent, "critical": False, "task": None})
            for agent in agents
        ]

        for step in steps:
            agent = step.agent
            task_id = getattr(getattr(step, "task", None), "task_id", None) or uuid4().hex
            agent_id = self._agent_id(agent)
            self._record_event(
                context,
                "agent_start",
                agent=agent_id,
                task_id=task_id,
                payload={"critical": bool(getattr(step, "critical", False))},
            )
            if on_start:
                on_start(agent)

            result = self._execute_agent(agent, context, task_id=task_id)
            results.append(result)
            if on_result:
                on_result(result, agent)

            if result.status == "success":
                self._record_event(
                    context,
                    "agent_success",
                    agent=agent_id,
                    task_id=task_id,
                    status=result.status,
                    payload={"attempts": result.attempts, "duration_ms": result.duration_ms},
                )
            else:
                self._record_event(
                    context,
                    "agent_failure",
                    agent=agent_id,
                    task_id=task_id,
                    status=result.status,
                    payload={
                        "attempts": result.attempts,
                        "retryable": result.retryable,
                        "errors": result.errors,
                    },
                )

            if (
                result.status == "failed"
                and getattr(step, "critical", False)
                and self.recovery_policy.stop_on_critical_failure
            ):
                logger.error(
                    "Stopping autonomous plan after critical agent failure: %s",
                    result.agent,
                )
                self._record_event(
                    context,
                    "plan_stopped",
                    agent=agent_id,
                    task_id=task_id,
                    status="failed",
                    payload={"reason": "critical_agent_failure"},
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

    def _recovery_decision(self, message: str, attempt: int) -> RecoveryDecision:
        max_attempts = self.recovery_policy.max_retries + 1
        retryable = self._is_retryable(message)
        should_retry = retryable and attempt < max_attempts
        action = "retry" if should_retry else "fail"
        reason = (
            "Transient failure matches recovery policy"
            if should_retry
            else "Failure is terminal or retry budget is exhausted"
        )
        return RecoveryDecision(
            action=action,
            retryable=retryable,
            reason=reason,
            attempt=attempt,
            max_attempts=max_attempts,
        )

    def _execute_agent(self, agent, context, task_id: str) -> AgentResult:
        attempts = self.recovery_policy.max_retries + 1
        last_error = None
        started = perf_counter()

        for attempt in range(1, attempts + 1):
            self._record_event(
                context,
                "agent_attempt",
                agent=self._agent_id(agent),
                task_id=task_id,
                payload={"attempt": attempt, "max_attempts": attempts},
            )
            try:
                result = agent.run(context)
                if not isinstance(result, AgentResult):
                    result = AgentResult(
                        agent=self._agent_id(agent),
                        status="failed",
                        errors=["Agent returned an invalid result type"],
                    )
                if result.status == "success":
                    result.attempts = attempt
                    result.retryable = False
                    result.duration_ms = round((perf_counter() - started) * 1000, 3)
                    result.task_id = task_id
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

            decision = self._recovery_decision(last_error, attempt)
            self._record_event(
                context,
                "recovery_decision",
                agent=self._agent_id(agent),
                task_id=task_id,
                status="retrying" if decision.action == "retry" else "failed",
                payload=decision.as_dict(),
            )
            if decision.action != "retry":
                return AgentResult(
                    agent=self._agent_id(agent),
                    status="failed",
                    errors=[last_error or "agent execution failed after recovery attempts"],
                    attempts=attempt,
                    retryable=decision.retryable,
                    duration_ms=round((perf_counter() - started) * 1000, 3),
                    task_id=task_id,
                )

            if self.recovery_policy.backoff_seconds > 0:
                sleep(self.recovery_policy.backoff_seconds * attempt)

        return AgentResult(
            agent=self._agent_id(agent),
            status="failed",
            errors=[last_error or "agent execution failed after recovery attempts"],
            attempts=attempts,
            retryable=True,
            duration_ms=round((perf_counter() - started) * 1000, 3),
            task_id=task_id,
        )

    @staticmethod
    def _record_event(context, event_type, **kwargs):
        recorder = getattr(context, "record_event", None)
        if callable(recorder):
            try:
                recorder(event_type=event_type, **kwargs)
            except Exception:
                logger.exception("Unable to record orchestration event %s", event_type)
