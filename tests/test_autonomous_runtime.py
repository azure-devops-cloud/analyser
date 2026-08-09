from core.agent_orchestrator import AgentOrchestrator, RecoveryPolicy
from models.agent_result import AgentResult
from models.context import AgentContext


class FlakyAgent:
    agent_name = "flaky_agent"

    def __init__(self):
        self.calls = 0

    def run(self, context):
        self.calls += 1
        if self.calls == 1:
            return AgentResult(agent=self.agent_name, status="failed", errors=["temporary upstream failure"])
        return AgentResult(agent=self.agent_name, status="success", data={"ok": True})


def test_recovery_records_attempts_and_lifecycle_events():
    context = AgentContext(run_id="run-1")
    agent = FlakyAgent()

    result = AgentOrchestrator(
        RecoveryPolicy(max_retries=1, backoff_seconds=0)
    ).execute([agent], context)[0]

    assert result.ok
    assert result.attempts == 2
    assert result.task_id
    event_types = [event.event_type for event in context.events]
    assert event_types == [
        "agent_start",
        "agent_attempt",
        "recovery_decision",
        "agent_attempt",
        "agent_success",
    ]


def test_non_retryable_failure_is_terminal_without_extra_attempt():
    class BrokenAgent:
        def run(self, context):
            return AgentResult(agent="broken_agent", status="failed", errors=["invalid input"])

    context = AgentContext(run_id="run-2")
    result = AgentOrchestrator(
        RecoveryPolicy(max_retries=3, backoff_seconds=0)
    ).execute([BrokenAgent()], context)[0]

    assert result.status == "failed"
    assert result.attempts == 1
    assert result.retryable is False
    assert [event.event_type for event in context.events][-1] == "agent_failure"


def test_recovery_policy_rejects_invalid_values():
    try:
        RecoveryPolicy(max_retries=-1)
    except ValueError as exc:
        assert "max_retries" in str(exc)
    else:
        raise AssertionError("negative retry budget must be rejected")
