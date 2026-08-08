"""Synthesize auditable evidence without changing deterministic decisions."""

from collections import defaultdict
from typing import Any

from models.evidence import EvidencePacket, Evidence


class ReasonerService:
    """Produce an evidence-grounded explanation of an existing decision."""

    def _as_dict(self, item: Any) -> dict[str, Any] | None:
        data = item.as_dict() if hasattr(item, "as_dict") else item
        return data if isinstance(data, dict) else None

    def _quality(self, evidence: list[dict[str, Any]]) -> float:
        if not evidence:
            return 0.0
        checks = []
        for item in evidence:
            checks.append(bool(item.get("evidence_id")))
            checks.append(bool(item.get("source")))
            checks.append(bool(item.get("claim")))
            checks.append(0.0 <= float(item.get("strength", 0) or 0) <= 1.0)
        return round(sum(checks) / len(checks), 3)

    def _contradictions(self, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
        contradictions = []
        by_kind = defaultdict(list)
        for item in evidence:
            by_kind[item.get("kind", "unknown")].append(item)

        for kind, items in by_kind.items():
            bullish = [x for x in items if "BULLISH" in str(x.get("claim", "")).upper()]
            bearish = [x for x in items if "BEARISH" in str(x.get("claim", "")).upper()]
            if bullish and bearish:
                contradictions.append({
                    "kind": kind,
                    "type": "directional_conflict",
                    "evidence_ids": [x.get("evidence_id") for x in bullish + bearish],
                    "description": f"Conflicting bullish and bearish {kind} evidence.",
                })
        return contradictions

    def analyze(self, decision: dict[str, Any], evidence: list[Any] | None = None) -> dict[str, Any]:
        evidence = evidence or []
        asset = decision.get("name", "UNKNOWN")
        relevant = []
        for item in evidence:
            data = self._as_dict(item)
            if not data:
                continue
            metadata = data.get("metadata", {}) or {}
            if metadata.get("asset") == asset or data.get("asset") == asset:
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
            normalized = {
                "evidence_id": item.get("evidence_id"),
                "source": item.get("source"),
                "kind": kind,
                "claim": claim,
                "value": value,
                "strength": strength,
                "observed_at": item.get("observed_at"),
                "metadata": item.get("metadata", {}),
            }
            if kind == "technical":
                if "Trend is BULLISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value < 30):
                    supporting.append(normalized)
                elif "Trend is BEARISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value > 70):
                    opposing.append(normalized)
            elif kind == "momentum" and isinstance(value, (int, float)):
                if value > 1:
                    supporting.append(normalized)
                elif value < -1:
                    opposing.append(normalized)
            elif kind == "sentiment":
                positive = value.get("positive", 0) if isinstance(value, dict) else 0
                negative = value.get("negative", 0) if isinstance(value, dict) else 0
                if positive > negative:
                    supporting.append(normalized)
                elif negative > positive:
                    opposing.append(normalized)
            elif kind == "risk" and isinstance(value, (int, float)) and value > 40:
                opposing.append(normalized)
            elif kind == "macro":
                opposing.append(normalized)

        bias = decision.get("bias", "NEUTRAL")
        if bias == "BULLISH":
            stance = "supporting" if supporting else "weak"
        elif bias == "BEARISH":
            stance = "supporting" if opposing else "weak"
        else:
            stance = "mixed"

        packet = EvidencePacket(
            asset=asset,
            bias=bias,
            score=decision.get("score", 0),
            confidence=decision.get("confidence", "LOW"),
            supporting=[Evidence(**{**item, "observed_at": __import__("datetime").datetime.fromisoformat(item["observed_at"])}) if item.get("observed_at") else Evidence(**{k: v for k, v in item.items() if k in {"evidence_id", "source", "kind", "claim", "value", "strength", "metadata"}}) for item in supporting],
            opposing=[Evidence(**{**item, "observed_at": __import__("datetime").datetime.fromisoformat(item["observed_at"])}) if item.get("observed_at") else Evidence(**{k: v for k, v in item.items() if k in {"evidence_id", "source", "kind", "claim", "value", "strength", "metadata"}}) for item in opposing],
            data_quality=self._quality(relevant),
            contradictions=self._contradictions(relevant),
        )
        result = packet.to_dict()
        result["stance"] = stance
        result["reasoning"] = (
            f"{asset} is {bias} with score {decision.get('score', 0)}. "
            f"Evidence is {stance}; {len(supporting)} supporting and {len(opposing)} opposing signals were found."
        )
        result["evidence_by_kind"] = {kind: len(items) for kind, items in groups.items()}
        return result
