"""Capability-based discovery for the autonomous agent fleet."""

from collections.abc import Iterable

from models.agent_contracts import AgentMetadata, normalize_capabilities


class AgentRegistry:
    """Register and discover agents without coupling the planner to classes."""

    DEFAULTS = {
        "NewsCollectorAgent": ("observe", ("news.discovery", "rss.fetch"), True),
        "NewsIntelligenceAgent": ("understand", ("news.classify", "news.relevance"), False),
        "NewsSentimentAgent": ("understand", ("sentiment.analyze",), False),
        "FactValidationAgent": ("verify", ("facts.validate",), False),
        "VerificationAgent": ("verify", ("evidence.verify", "quality.score"), True),
        "DeduplicationAgent": ("understand", ("news.deduplicate",), False),
        "RankingAgent": ("decide", ("news.rank",), False),
        "MarketAgent": ("observe", ("market.observe",), False),
        "CalendarAgent": ("observe", ("macro.calendar",), False),
        "TechnicalAnalysisAgent": ("understand", ("market.technical",), False),
        "DecisionAgent": ("decide", ("market.decision",), True),
        "ReasonerAgent": ("reason", ("evidence.reason",), False),
        "ConfidenceAgent": ("verify", ("confidence.score",), False),
        "RiskAgent": ("decide", ("risk.assess",), False),
        "AlertAgent": ("execute", ("alert.generate",), False),
        "HistoryAgent": ("learn", ("history.persist",), False),
        "MonitoringAgent": ("observe", ("health.observe",), False),
        "SummaryAgent": ("execute", ("report.compose",), False),
    }

    def __init__(self, agents: Iterable | None = None):
        self._agents: dict[str, object] = {}
        for agent in agents or ():
            self.register(agent)

    @classmethod
    def metadata_for(cls, agent: object) -> AgentMetadata:
        describe = getattr(agent, "describe", None)
        if callable(describe):
            metadata = describe()
            if isinstance(metadata, AgentMetadata) and (
                metadata.capabilities or metadata.phase != "execute" or metadata.critical
            ):
                return metadata

        class_name = agent.__class__.__name__
        phase, capabilities, critical = cls.DEFAULTS.get(
            class_name,
            (
                getattr(agent, "phase", "execute"),
                getattr(agent, "capabilities", ()),
                getattr(agent, "critical", False),
            ),
        )
        name = getattr(agent, "agent_name", None) or class_name
        return AgentMetadata(
            name=str(name),
            phase=str(phase),
            capabilities=normalize_capabilities(capabilities),
            critical=bool(critical),
            version=str(getattr(agent, "version", "1")),
        )

    def register(self, agent: object) -> AgentMetadata:
        metadata = self.metadata_for(agent)
        if metadata.name in self._agents and self._agents[metadata.name] is not agent:
            raise ValueError(f"Agent name already registered: {metadata.name}")
        self._agents[metadata.name] = agent
        return metadata

    def get(self, name: str) -> object:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc

    def all(self) -> tuple[object, ...]:
        return tuple(self._agents.values())

    def metadata(self) -> tuple[AgentMetadata, ...]:
        return tuple(self.metadata_for(agent) for agent in self._agents.values())

    def find_by_capability(self, capability: str) -> tuple[object, ...]:
        target = capability.strip().lower()
        return tuple(
            agent
            for agent in self._agents.values()
            if target in self.metadata_for(agent).capabilities
        )
