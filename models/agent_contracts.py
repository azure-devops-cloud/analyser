"""Typed contracts shared by the autonomous agent runtime.

The runtime deliberately keeps intelligence decisions inside agents while the
contracts make execution state, capabilities, and recovery decisions explicit
and machine-readable.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class AgentMetadata:
    """Stable capability and safety metadata exposed by an agent."""

    name: str
    phase: str = "execute"
    capabilities: tuple[str, ...] = ()
    critical: bool = False
    version: str = "1"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AgentTask:
    """A traceable task delegated by the control plane to one agent."""

    agent: str
    phase: str
    run_id: str
    task_id: str = field(default_factory=lambda: uuid4().hex)
    inputs: Mapping[str, Any] = field(default_factory=dict)
    attempt: int = 1
    parent_task_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AgentEvent:
    """Immutable lifecycle event used for auditability and future tracing."""

    event_type: str
    run_id: str
    agent: str | None = None
    task_id: str | None = None
    status: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Deterministic recovery decision recorded after an agent failure."""

    action: str
    retryable: bool
    reason: str
    attempt: int
    max_attempts: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_capabilities(values: Sequence[str] | None) -> tuple[str, ...]:
    """Normalize capability names into stable, deduplicated identifiers."""
    return tuple(dict.fromkeys(str(value).strip().lower() for value in (values or ()) if str(value).strip()))
