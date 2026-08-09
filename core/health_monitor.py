"""Deterministic runtime health assessment used by the monitoring agent."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class HealthSignal:
    component: str
    status: str
    message: str
    severity: str = "info"
    observed_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "severity": self.severity,
            "observed_at": self.observed_at,
        }


class HealthMonitor:
    def assess(self, results: Iterable[Any], context: Any, tool_snapshot: dict[str, Any] | None = None) -> list[HealthSignal]:
        now = datetime.now(timezone.utc).isoformat()
        signals: list[HealthSignal] = []
        for result in results:
            status = getattr(result, "status", None)
            agent = getattr(result, "agent", "unknown")
            if status == "success":
                signals.append(HealthSignal(agent, "healthy", "agent completed successfully", observed_at=now))
            else:
                signals.append(HealthSignal(agent, "degraded", "; ".join(getattr(result, "errors", [])) or "agent failed", "error", now))
        for name, stats in (tool_snapshot or {}).items():
            failures = int(stats.get("failures", 0))
            signals.append(HealthSignal(name, "degraded" if failures else "healthy", f"tool calls={stats.get('calls', 0)}, failures={failures}", "warning" if failures else "info", now))
        if getattr(context, "errors", None):
            signals.append(HealthSignal("workflow", "degraded", f"{len(context.errors)} workflow errors recorded", "warning", now))
        return signals
