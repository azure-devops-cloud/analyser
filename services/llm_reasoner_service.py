import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LLMReasonerService:
    """Optional LLM synthesis layer; deterministic evidence remains authoritative."""

    def __init__(self, client=None):
        self.client = client

    def build_prompt(self, packet: Dict[str, Any]) -> str:
        return (
            "You are a market-intelligence explanation assistant. "
            "Use only the supplied evidence. Do not invent facts. "
            "Do not change score, bias, confidence, or evidence IDs. "
            "Return JSON with keys: summary, key_points, cited_evidence_ids.\n\n"
            f"Evidence packet:\n{json.dumps(packet, sort_keys=True, default=str)}"
        )

    def synthesize(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        if self.client is None:
            return self._fallback(packet)

        try:
            response = self.client(self.build_prompt(packet))
            parsed = response if isinstance(response, dict) else json.loads(response)
            return self._validate(parsed, packet)
        except Exception as exc:
            logger.warning("LLM reasoner unavailable; using deterministic fallback: %s", exc)
            return self._fallback(packet)

    def _validate(self, result: Dict[str, Any], packet: Dict[str, Any]) -> Dict[str, Any]:
        allowed_ids = {item["evidence_id"] for item in packet.get("supporting", []) + packet.get("opposing", [])}
        cited = [str(item) for item in result.get("cited_evidence_ids", [])]
        cited = [item for item in cited if item in allowed_ids]
        return {
            "summary": str(result.get("summary", "")),
            "key_points": [str(item) for item in result.get("key_points", [])][:5],
            "cited_evidence_ids": cited,
            "asset": packet.get("asset"),
            "score": packet.get("score"),
            "bias": packet.get("bias"),
        }

    def _fallback(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        stance = packet.get("stance", "weak")
        summary = (
            f"{packet.get('asset', 'Market')} is {packet.get('bias', 'UNKNOWN')} "
            f"with {packet.get('evidence_count', 0)} supporting evidence item(s); "
            f"evidence stance is {stance}."
        )
        return self._validate(
            {
                "summary": summary,
                "key_points": [item.get("claim", "") for item in packet.get("supporting", [])[:5]],
                "cited_evidence_ids": [item.get("evidence_id") for item in packet.get("supporting", [])],
            },
            packet,
        )
