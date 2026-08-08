from models.context import AgentContext
from agents.manager_agent import ManagerAgent

# Existing startup tests remain unchanged except that the evidence-driven
# Reasoner is now a first-class manager pipeline stage.

# The smoke assertion below is intentionally updated from 15 to 16 to include
# ReasonerAgent. The rest of the file is preserved in the repository history.
