from agents.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from models.agent_contracts import AgentTask, normalize_capabilities
from models.agent_result import AgentResult
from models.context import AgentContext


class ResearchAgent(BaseAgent):
    agent_name = "research_agent"
    phase = "understand"
    capabilities = ("Web.Search", "web.search")

    def run(self, context):
        return AgentResult(agent=self.agent_name, status="success")


def test_capabilities_are_normalized_and_deduplicated():
    assert normalize_capabilities([" Web.Search ", "web.search", "", "RAG"]) == (
        "web.search",
        "rag",
    )


def test_registry_discovers_typed_agent_metadata():
    agent = ResearchAgent()
    registry = AgentRegistry([agent])
    metadata = registry.metadata()[0]

    assert metadata.name == "research_agent"
    assert metadata.phase == "understand"
    assert metadata.capabilities == ("web.search",)
    assert registry.find_by_capability("WEB.SEARCH") == (agent,)


def test_context_records_traceable_events_and_tool_results():
    context = AgentContext(run_id="run-1")
    context.record_event(event_type="agent_start", agent="research_agent")
    context.record_tool_result("search", {"items": 3})
    context.set_metadata("plan_id", "plan-1")

    snapshot = context.snapshot()
    assert snapshot["run_id"] == "run-1"
    assert snapshot["event_count"] == 1
    assert snapshot["tool_count"] == 1
    assert context.events[0].run_id == "run-1"
    assert context.metadata["plan_id"] == "plan-1"


def test_agent_task_is_traceable():
    task = AgentTask(agent="research_agent", phase="understand", run_id="run-1")
    payload = task.as_dict()

    assert payload["agent"] == "research_agent"
    assert payload["run_id"] == "run-1"
    assert payload["task_id"]
