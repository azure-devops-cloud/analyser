from core.agent_orchestrator import AgentOrchestrator, RecoveryPolicy
from models.agent_result import AgentResult


class FlakyAgent:
    def __init__(self):
        self.calls = 0

    def run(self, context):
        self.calls += 1
        if self.calls == 1:
            return AgentResult(agent="flaky_agent", status="failed", errors=["temporary failure"])
        return AgentResult(agent="flaky_agent", status="success", data={"ok": True}, count=1)


def test_orchestrator_recovers_from_transient_agent_failure():
    agent = FlakyAgent()
    events = []

    results = AgentOrchestrator(
        RecoveryPolicy(max_retries=1, backoff_seconds=0)
    ).execute(
        [agent],
        object(),
        on_start=lambda current: events.append(("start", current)),
        on_result=lambda result, current: events.append(("result", result.status)),
    )

    assert agent.calls == 2
    assert results[0].status == "success"
    assert events[0][0] == "start"
    assert events[-1] == ("result", "success")


def test_orchestrator_returns_terminal_failure_after_retry_budget():
    class BrokenAgent:
        def run(self, context):
            raise RuntimeError("upstream unavailable")

    result = AgentOrchestrator(
        RecoveryPolicy(max_retries=1, backoff_seconds=0)
    ).execute([BrokenAgent()], object())[0]

    assert result.status == "failed"
    assert "upstream unavailable" in result.errors[0]
