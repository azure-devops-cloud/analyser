from dataclasses import dataclass
from typing import Any, List


@dataclass
class AgentResult:
    agent: str
    status: str
    data: Any = None
    count: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
