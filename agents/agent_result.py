from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResult:

    agent: str

    status: str

    data: Any = None

    count: int = 0

    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
