from abc import ABC, abstractmethod

from models.agent_contracts import AgentMetadata, normalize_capabilities


class BaseAgent(ABC):
    """Base contract for autonomous agents.

    Agents own intelligence and domain behavior. The runtime consumes only
    stable metadata and the typed ``run`` contract for orchestration, safety,
    recovery, and observability.
    """

    agent_name = ""
    phase = "execute"
    capabilities = ()
    critical = False
    version = "1"

    def describe(self) -> AgentMetadata:
        name = self.agent_name or self.__class__.__name__
        return AgentMetadata(
            name=name,
            phase=self.phase,
            capabilities=normalize_capabilities(self.capabilities),
            critical=self.critical,
            version=self.version,
        )

    @abstractmethod
    def run(self, context):
        """Execute the agent against shared ``AgentContext`` state."""
        raise NotImplementedError
