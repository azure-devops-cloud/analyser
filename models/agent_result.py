from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Structured outcome returned by every agent execution."""

    agent: str
    status: str
    data: Any = None
    count: int = 0
    errors: list[str] = field(default_factory=list)
    attempts: int = 1
    retryable: bool = False
    duration_ms: float | None = None
    task_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == "success"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
