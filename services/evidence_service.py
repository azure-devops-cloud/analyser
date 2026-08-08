"""Build deterministic, auditable evidence for downstream reasoning."""

from hashlib import sha1
from typing import Any

from models.evidence import Evidence


class EvidenceService:
    """Convert trusted pipeline outputs into normalized evidence records."""

    def build(self, market: dict[str, Any], sentiment: dict[str, Any] | None = None,
              calendar_events: list[Any] | None = None,
              fact_validation: dict[str, Any] | None = None) -> list[Evidence]:
        sentiment = sentiment or {}
        calendar_events = calendar_events or []
        fact_validation = fact_validation or {}
        name = market.get("name", "unknown")
        evidence: list[Evidence] = []

        def add(kind: str, claim: str, value: Any, strength: float, source: str) -> None:
            raw = f"{name}|{kind}|{claim}|{value}"
            evidence.append(Evidence(
                evidence_id=f"ev-{sha1(raw.encode()).hexdigest()[:12]}",
                source=source,
                kind=kind,
                claim=claim,
                value=value,
                strength=strength,
                metadata={"asset": name},
            ))

        trend = market.get("trend", "SIDEWAYS")
        add("technical", f"Trend is {trend}", trend, 0.85, "market_data")

        rsi = market.get("rsi", 50)
        add("technical", f"RSI is {rsi}", rsi, 0.85, "market_data")

        daily = market.get("daily_change", 0)
        add("momentum", f"Daily change is {daily}%", daily, 0.8, "market_data")

        volatility = market.get("volatility", 0)
        add("risk", f"Volatility is {volatility}", volatility, 0.8, "market_data")

        positive = sentiment.get("positive", 0)
        negative = sentiment.get("negative", 0)
        sentiment_strength = min(1.0, abs(positive - negative) / max(1, positive + negative))
        add("sentiment", f"News sentiment is {positive} positive vs {negative} negative",
            {"positive": positive, "negative": negative}, sentiment_strength, "news_sentiment")

        if calendar_events:
            add("macro", f"{len(calendar_events)} economic event(s) are ahead",
                len(calendar_events), 0.7, "economic_calendar")

        validation_score = fact_validation.get("confidence_score", 0)
        if validation_score:
            add("validation", "News corroboration confidence is available",
                validation_score, min(1.0, validation_score / 100), "fact_validation")

        return evidence
