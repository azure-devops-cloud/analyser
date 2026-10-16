"""Explicit, capability-scoped tool registry for autonomous agents.

The registry is deliberately deterministic: agents may select only registered
read/transform tools and never receive arbitrary shell execution.
"""

from dataclasses import dataclass
from time import monotonic, sleep
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    capability: str
    handler: Callable[..., Any]
    timeout_seconds: float = 30.0
    max_retries: int = 1
    side_effect: bool = False


class ToolExecutionError(RuntimeError):
    """Raised when a registered tool cannot complete safely."""


class ToolRegistry:
    """Capability-based tool registry with bounded retry and timing metadata."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self._stats: dict[str, dict[str, Any]] = {}

    def register(self, spec: ToolSpec) -> None:
        if not spec.name.strip() or not spec.capability.strip():
            raise ValueError("tool name and capability are required")
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        if spec.max_retries < 0 or spec.timeout_seconds <= 0:
            raise ValueError("invalid tool retry/timeout policy")
        self._tools[spec.name] = spec
        self._stats[spec.name] = {"calls": 0, "failures": 0, "last_error": None}

    def discover(self, capability: str) -> tuple[ToolSpec, ...]:
        target = capability.strip().lower()
        return tuple(spec for spec in self._tools.values() if spec.capability.lower() == target)

    def execute(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise ToolExecutionError(f"unregistered tool: {name}")
        spec = self._tools[name]
        stats = self._stats[name]
        last_error: Exception | None = None
        for attempt in range(spec.max_retries + 1):
            stats["calls"] += 1
            started = monotonic()
            try:
                result = spec.handler(**kwargs)
                elapsed = monotonic() - started
                if elapsed > spec.timeout_seconds:
                    raise TimeoutError(f"tool {name} exceeded {spec.timeout_seconds:.1f}s timeout")
                return result
            except Exception as exc:  # bounded by explicit retry policy
                last_error = exc
                stats["failures"] += 1
                stats["last_error"] = str(exc)
                if attempt >= spec.max_retries:
                    break
                sleep(min(2 ** attempt, 5))
        raise ToolExecutionError(f"tool {name} failed: {last_error}") from last_error

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {name: dict(stats) for name, stats in self._stats.items()}

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)
