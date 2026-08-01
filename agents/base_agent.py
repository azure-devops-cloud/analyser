from abc import ABC, abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def run(self, context):
        """
        Execute the agent.

        Parameters
        ----------
        context : AgentContext
            Shared context between all agents.
        """
        pass
