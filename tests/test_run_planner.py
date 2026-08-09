from core.agent_orchestrator import AgentOrchestrator, RecoveryPolicy
from core.run_planner import RunPlanner
from models.agent_result import AgentResult


class NewsCollectorAgent:
    def run(self, context):
        return AgentResult(agent="news_collector_agent", status="success", count=1)


class VerificationAgent:
    def run(self, context):
        return AgentResult(agent="verification_agent", status="success", count=1)


class UnknownAgent:
    def run(self, context):
        return AgentResult(agent="unknown_agent", status="success")


def test_run_planner_builds_auditable_dependency_safe_plan():
    agents = [NewsCollectorAgent(), VerificationAgent(), UnknownAgent()]

    plan = RunPlanner().plan(agents, {})

    assert plan.mode == "autonomous"
    assert plan.agent_names == [
        "NewsCollectorAgent",
        "VerificationAgent",
        "UnknownAgent",
    ]
    assert plan.steps[0].phase == "observe"
    assert plan.steps[0].critical is True
    assert plan.steps[1].phase == "verify"
    assert plan.steps[1].critical is True
    assert plan.steps[2].phase == "execute"
    assert plan.steps[2].critical is False


def test_orchestrator_retries_only_retryable_failures():
    class ValidationFailure:
        def __init__(self):
            self.calls = 0

        def run(self, context):
            self.calls += 1
            return AgentResult(
                agent="validation_failure",
                status="failed",
                errors=["invalid schema"],
            )

    agent = ValidationFailure()
    result = AgentOrchestrator(
        RecoveryPolicy(max_retries=2, backoff_seconds=0)
    ).execute([agent], object())[0]

    assert result.status == "failed"
    assert agent.calls == 1


def test_orchestrator_retries_transient_unavailable_failure():
    class UnavailableOnce:
        def __init__(self):
            self.calls = 0

        def run(self, context):
            self.calls += 1
            if self.calls == 1:
                return AgentResult(
                    agent="provider_agent",
                    status="failed",
                    errors=["provider unavailable"],
                )
            return AgentResult(
                agent="provider_agent",
                status="success",
                count=1,
            )

    agent = UnavailableOnce()
    result = AgentOrchestrator(
        RecoveryPolicy(max_retries=1, backoff_seconds=0)
    ).execute([agent], object())[0]

    assert result.status == "success"
    assert agent.calls == 2


def test_orchestrator_can_stop_after_critical_plan_failure():
    class BrokenCritical:
        def run(self, context):
            return AgentResult(
                agent="critical_agent",
                status="failed",
                errors=["upstream unavailable"],
            )

    class ShouldNotRun:
        def run(self, context):
            raise AssertionError("downstream agent must not run")

    planner = RunPlanner()
    critical = BrokenCritical()
    downstream = ShouldNotRun()
    plan = planner.plan([critical, downstream], {})

    # Explicitly mark the first step critical for this synthetic agent.
    plan = type(plan)(
        mode=plan.mode,
        reason=plan.reason,
        steps=(
            type(plan.steps[0])(
                agent=critical,
                phase="verify",
                critical=True,
                tags=("verify",),
            ),
            plan.steps[1],
        ),
    )

    results = AgentOrchestrator(
        RecoveryPolicy(
            max_retries=0,
            backoff_seconds=0,
            stop_on_critical_failure=True,
        )
    ).execute([critical, downstream], object(), plan=plan)

    assert len(results) == 1
    assert results[0].status == "failed"
