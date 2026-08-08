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


@dataclass
class EvidencePacket:
    """Canonical reasoning input; decisions remain authoritative elsewhere."""

    asset: str
    bias: str
    score: float
    confidence: Any = None
    supporting: list[Evidence] = field(default_factory=list)
    opposing: list[Evidence] = field(default_factory=list)
    data_quality: float = 0.0
    contradictions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def evidence_count(self) -> int:
        return len(self.supporting) + len(self.opposing)

    def as_dict(self) -> dict[str, Any]:
        return {
            "asset": self.asset,
            "bias": self.bias,
            "score": self.score,
            "confidence": self.confidence,
            "supporting": [item.as_dict() for item in self.supporting],
            "opposing": [item.as_dict() for item in self.opposing],
            "evidence_count": self.evidence_count,
            "data_quality": round(max(0.0, min(1.0, self.data_quality)), 3),
            "contradictions": list(self.contradictions),
        }

    # Backward-compatible alias for callers using the pre-canonical contract.
    def to_dict(self) -> dict[str, Any]:
        return self.as_dict()
