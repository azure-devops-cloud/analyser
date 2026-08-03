"""Typed domain contracts shared by agents, services, and persistence."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AgentStatus(StrEnum):
    """Allowed lifecycle states for an agent execution."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class RiskLevel(StrEnum):
    """Normalized risk levels used by future risk and portfolio agents."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class Article:
    """Normalized news article collected from an external source."""

    title: str
    link: str
    source: str
    published_at: str = ""
    summary: str = ""
    category: str = "GENERAL"
    impact_score: int = 0
    sentiment_score: int = 0


@dataclass(frozen=True, slots=True)
class MarketObservation:
    """A point-in-time price and technical state for one instrument."""

    name: str
    symbol: str
    price: float
    captured_at: datetime
    daily_change: float = 0.0
    trend: str = "SIDEWAYS"
    signal: str = "HOLD"
    rsi: float = 50.0
    volatility: float = 0.0


@dataclass(frozen=True, slots=True)
class Decision:
    """Explainable recommendation emitted by the decision engine."""

    name: str
    bias: str
    confidence: str
    score: int
    reasons: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionMetric:
    """One measurable agent execution event."""

    run_id: str
    agent: str
    status: AgentStatus
    started_at: datetime
    duration_ms: float
    item_count: int = 0
    error_count: int = 0
