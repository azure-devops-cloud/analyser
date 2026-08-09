from typing import Any
from uuid import uuid4

from models.agent_contracts import AgentEvent


class AgentContext:
    """Shared run state with typed lifecycle events and auditable evidence."""

    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or uuid4().hex
        self.state_version = 1
        self.news = []
        self.news_intelligence = []
        self.market = []
        self.decisions = []
        self.calendar = []
        self.calendar_status = {}
        self.errors = []
        self.news_sentiment = {}
        self.fact_validation = {}
        self.source_trust_map = {}
        self.alerts = []
        self.history = {}
        self.execution = {}
        self.technical_analysis = []
        self.confidence = {}
        self.risk = {}
        self.evidence = []
        self.reasoning = []
        self.events: list[AgentEvent] = []
        self.tool_results: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}

    def record_event(self, event: AgentEvent | None = None, **kwargs) -> None:
        """Append an immutable lifecycle event to the current run."""
        if event is None:
            event = AgentEvent(run_id=self.run_id, **kwargs)
        elif event.run_id != self.run_id:
            raise ValueError("Event run_id does not match context run_id")
        self.events.append(event)

    def record_tool_result(self, tool_name: str, result: Any) -> None:
        """Store the latest result for a named deterministic tool."""
        self.tool_results[tool_name] = result

    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def add_news(self, news):
        self.news = news

    def add_news_intelligence(self, intelligence):
        self.news_intelligence = intelligence or []

    def add_market(self, market):
        self.market = market

    def add_decisions(self, decisions):
        self.decisions = decisions

    def add_calendar(self, calendar):
        self.calendar = calendar

    def add_calendar_status(self, status):
        self.calendar_status = status or {}

    def add_error(self, error):
        self.errors.append(error)

    def add_news_sentiment(self, data):
        self.news_sentiment = data

    def add_fact_validation(self, data):
        self.fact_validation = data

    def add_source_trust_map(self, data):
        self.source_trust_map = data

    def add_alerts(self, alerts):
        self.alerts = alerts

    def add_history(self, history):
        self.history = history

    def add_execution(self, execution):
        self.execution = execution

    def add_technical_analysis(self, analysis):
        self.technical_analysis = analysis

    def add_confidence(self, confidence):
        self.confidence = confidence

    def add_risk(self, risk):
        self.risk = risk

    def add_evidence(self, evidence):
        """Append auditable evidence records to the current run."""
        if not evidence:
            return
        self.evidence.extend(evidence)

    def add_reasoning(self, reasoning):
        """Store evidence-grounded reasoning without mutating decisions."""
        self.reasoning = reasoning or []

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable control-plane snapshot without private state."""
        return {
            "run_id": self.run_id,
            "state_version": self.state_version,
            "news_count": len(self.news),
            "news_intelligence_count": len(self.news_intelligence),
            "market_count": len(self.market),
            "decision_count": len(self.decisions),
            "evidence_count": len(self.evidence),
            "reasoning_count": len(self.reasoning),
            "event_count": len(self.events),
            "tool_count": len(self.tool_results),
            "error_count": len(self.errors),
        }
