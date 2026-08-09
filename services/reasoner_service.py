"""Synthesize auditable evidence without changing deterministic decisions."""

from collections import defaultdict
from datetime import datetime
from typing import Any

from models.evidence import Evidence, EvidencePacket


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
            checks.extend([
                bool(item.get("evidence_id")), bool(item.get("source")),
                bool(item.get("claim")), 0.0 <= float(item.get("strength", 0) or 0) <= 1.0,
            ])
        return round(sum(checks) / len(checks), 3)

    def _contradictions(self, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_kind = defaultdict(lambda: {"supporting": [], "opposing": []})
        for item in evidence:
            claim = str(item.get("claim", "")).upper()
            kind = item.get("kind", "unknown")
            if "BULLISH" in claim:
                by_kind[kind]["supporting"].append(item)
            elif "BEARISH" in claim:
                by_kind[kind]["opposing"].append(item)
        result = []
        for kind, sides in by_kind.items():
            if sides["supporting"] and sides["opposing"]:
                ids = [x.get("evidence_id") for x in sides["supporting"] + sides["opposing"]]
                result.append({
                    "kind": kind, "type": "directional_conflict",
                    "evidence_ids": [x for x in ids if x],
                    "severity": "HIGH" if len(ids) >= 3 else "MEDIUM",
                    "description": f"Conflicting bullish and bearish {kind} evidence.",
                })
        return result

    def _to_evidence(self, item: dict[str, Any]) -> Evidence:
        observed_at = item.get("observed_at")
        if isinstance(observed_at, str):
            try:
                observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
            except ValueError:
                observed_at = None
        kwargs = {
            "evidence_id": str(item.get("evidence_id", "")),
            "source": str(item.get("source") or "unknown"),
            "kind": str(item.get("kind", "unknown")),
            "claim": str(item.get("claim", "")),
            "value": item.get("value"),
            "strength": float(item.get("strength", 0) or 0),
            "metadata": dict(item.get("metadata", {}) or {}),
        }
        if observed_at is not None:
            kwargs["observed_at"] = observed_at
        return Evidence(**kwargs)

    def _reasoning_confidence(self, quality: float, evidence_count: int, contradictions: list[dict[str, Any]]) -> float:
        """Confidence for the explanation layer only; never the deterministic decision."""
        if evidence_count == 0:
            return 0.0
        base = quality * 100.0
        if contradictions:
            severity_penalty = sum(20.0 if item.get("severity") == "HIGH" else 10.0 for item in contradictions)
            base -= min(40.0, severity_penalty)
        return round(max(0.0, min(100.0, base)), 1)

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

        supporting, opposing = [], []
        for item in relevant:
            claim, value = item.get("claim", ""), item.get("value")
            normalized = {
                "evidence_id": item.get("evidence_id"), "source": item.get("source") or "unknown",
                "kind": item.get("kind", "unknown"), "claim": claim, "value": value,
                "strength": float(item.get("strength", 0) or 0), "observed_at": item.get("observed_at"),
                "metadata": item.get("metadata", {}),
            }
            kind = normalized["kind"]
            if kind == "technical":
                if "Trend is BULLISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value < 30): supporting.append(normalized)
                elif "Trend is BEARISH" in claim or ("RSI is" in claim and isinstance(value, (int, float)) and value > 70): opposing.append(normalized)
            elif kind == "momentum" and isinstance(value, (int, float)):
                if value > 1: supporting.append(normalized)
                elif value < -1: opposing.append(normalized)
            elif kind == "sentiment" and isinstance(value, dict):
                if value.get("positive", 0) > value.get("negative", 0): supporting.append(normalized)
                elif value.get("negative", 0) > value.get("positive", 0): opposing.append(normalized)
            elif kind == "risk" and isinstance(value, (int, float)) and value > 40: opposing.append(normalized)
            elif kind == "macro": opposing.append(normalized)

        bias = decision.get("bias", "NEUTRAL")
        if bias == "BULLISH": stance = "supporting" if supporting else "weak"
        elif bias == "BEARISH": stance = "supporting" if opposing else "weak"
        else: stance = "mixed"

        contradictions = self._contradictions(relevant)
        evidence_status = "CONFLICTED" if contradictions else ("SUPPORTED" if supporting or opposing else "INSUFFICIENT")
        packet = EvidencePacket(
            asset=asset, bias=bias, score=decision.get("score", 0), confidence=decision.get("confidence", "LOW"),
            supporting=[self._to_evidence(item) for item in supporting],
            opposing=[self._to_evidence(item) for item in opposing],
            data_quality=self._quality(relevant), contradictions=contradictions,
        )
        result = packet.as_dict()
        reasoning_confidence = self._reasoning_confidence(
            result.get("data_quality", 0.0), result.get("evidence_count", 0), contradictions
        )
        result.update({
            "stance": stance,
            "evidence_status": evidence_status,
            "reasoning_confidence": reasoning_confidence,
            "reasoning_confidence_basis": {
                "data_quality": result.get("data_quality", 0.0),
                "evidence_count": result.get("evidence_count", 0),
                "contradiction_count": len(contradictions),
            },
            "reasoning": f"{asset} is {bias} with score {decision.get('score', 0)}. Evidence is {stance}; {len(supporting)} supporting and {len(opposing)} opposing signals were found.",
            "evidence_by_kind": {kind: len(items) for kind, items in groups.items()},
        })
        return result
