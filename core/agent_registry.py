"""Capability-based discovery for the autonomous agent fleet."""

from collections.abc import Iterable

from models.agent_contracts import AgentMetadata, normalize_capabilities


class AgentRegistry:
    """Register and discover agents without coupling the planner to classes."""

    def __init__(self, agents: Iterable | None = None):
        self._agents: dict[str, object] = {}
        for agent in agents or ():
            self.register(agent)

    @staticmethod
    def metadata_for(agent: object) -> AgentMetadata:
        describe = getattr(agent, "describe", None)
        if callable(describe):
            metadata = describe()
            if isinstance(metadata, AgentMetadata):
                return metadata

        name = getattr(agent, "agent_name", None)
        if not name:
            name = agent.__class__.__name__
        return AgentMetadata(
            name=str(name),
            phase=str(getattr(agent, "phase", "execute")),
            capabilities=normalize_capabilities(getattr(agent, "capabilities", ())),
            critical=bool(getattr(agent, "critical", False)),
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
