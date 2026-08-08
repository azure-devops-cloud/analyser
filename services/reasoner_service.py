"""Synthesize auditable evidence without changing deterministic decisions."""

from collections import defaultdict
from typing import Any


class ReasonerService:
    """Produce an evidence-grounded explanation of an existing decision.

    This first version is deterministic by design: it does not invent facts and
    never changes the legacy decision score or bias. A future LLM reasoner can
    consume this normalized packet without becoming the source of truth.
    """

    def analyze(self, decision: dict[str, Any], evidence: list[Any] | None = None) -> dict[str, Any]:
        evidence = evidence or []
        asset = decision.get("name", "UNKNOWN")
        relevant = []
        for item in evidence:
            data = item.as_dict() if hasattr(item, "as_dict") else item
            if not isinstance(data, dict):
                continue
            if data.get("metadata", {}).get("asset") == asset:
                relevant.append(data)

        groups = defaultdict(list)
        for item in relevant:
            groups[item.get("kind", "unknown")].append(item)

        supporting = []
        opposing = []
        for item in relevant:
            claim = item.get("claim", "")
            strength = float(item.get("strength", 0) or 0)
            kind = item.get("kind", "unknown")
            value = item.get("value")
            text = f"{claim} (strength {strength:.2f})"
            if kind == "technical":
                if "Trend is BULLISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value < 30):
                    supporting.append(text)
                elif "Trend is BEARISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value > 70):
                    opposing.append(text)
            elif kind == "momentum" and isinstance(value, (int, float)):
                if value > 1:
                    supporting.append(text)
                elif value < -1:
                    opposing.append(text)
            elif kind == "sentiment":
                positive = value.get("positive", 0) if isinstance(value, dict) else 0
                negative = value.get("negative", 0) if isinstance(value, dict) else 0
                if positive > negative:
                    supporting.append(text)
                elif negative > positive:
                    opposing.append(text)
            elif kind == "risk" and isinstance(value, (int, float)) and value > 40:
                opposing.append(text)
            elif kind == "macro":
                opposing.append(text)

        bias = decision.get("bias", "NEUTRAL")
        if bias == "BULLISH":
            stance = "supporting" if supporting else "weak"
        elif bias == "BEARISH":
            stance = "supporting" if opposing else "weak"
        else:
            stance = "mixed"

        return {
            "asset": asset,
            "bias": bias,
            "score": decision.get("score", 0),
            "confidence": decision.get("confidence", "LOW"),
            "stance": stance,
            "evidence_count": len(relevant),
            "evidence_by_kind": {kind: len(items) for kind, items in groups.items()},
            "supporting": supporting,
            "opposing": opposing,
            "reasoning": (
                f"{asset} is {bias} with score {decision.get('score', 0)}. "
                f"Evidence is {stance}; {len(supporting)} supporting and {len(opposing)} opposing signals were found."
            ),
        }
