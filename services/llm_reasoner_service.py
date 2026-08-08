import json
import logging
from typing import Any, Dict

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

    @staticmethod
    def _evidence_id(item: Any) -> str | None:
        if isinstance(item, dict):
            value = item.get("evidence_id")
            return str(value) if value is not None else None
        return None

    @staticmethod
    def _claim(item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("claim", ""))
        return str(item)

    def _validate(self, result: Dict[str, Any], packet: Dict[str, Any]) -> Dict[str, Any]:
        evidence_items = packet.get("supporting", []) + packet.get("opposing", [])
        allowed_ids = {
            evidence_id
            for evidence_id in (self._evidence_id(item) for item in evidence_items)
            if evidence_id
        }
        cited = [str(item) for item in result.get("cited_evidence_ids", [])]
        cited = [item for item in cited if not allowed_ids or item in allowed_ids]

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
        supporting = packet.get("supporting", [])
        summary = (
            f"{packet.get('asset', 'Market')} is {packet.get('bias', 'UNKNOWN')} "
            f"with {packet.get('evidence_count', 0)} supporting evidence item(s); "
            f"evidence stance is {stance}."
        )
        return self._validate(
            {
                "summary": summary,
                "key_points": [self._claim(item) for item in supporting[:5]],
                "cited_evidence_ids": [self._evidence_id(item) for item in supporting if self._evidence_id(item)],
            },
            packet,
        )
