"""Typed evidence contracts for explainable market decisions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class Evidence:
    """One auditable fact or signal used by the decision engine."""

    evidence_id: str
    source: str
    kind: str
    claim: str
    value: Any = None
    strength: float = 0.0
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "kind": self.kind,
            "claim": self.claim,
            "value": self.value,
            "strength": round(max(0.0, min(1.0, self.strength)), 3),
            "observed_at": self.observed_at.isoformat(),
            "metadata": self.metadata,
        }
