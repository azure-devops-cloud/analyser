from datetime import datetime, timezone
from urllib.parse import urlparse


class VerificationService:
    """Deterministically verify news evidence quality and recovery needs."""

    STATES = {"verified", "partially_verified", "needs_verification", "degraded"}

    def verify(self, articles=None, evidence=None, intelligence=None, source_trust=None):
        articles = articles or []
        evidence = evidence or []
        intelligence = intelligence or []
        source_trust = source_trust or {}

        source_ids = set()
        for article in articles:
            source = article.get("source") or article.get("link", "")
            source_id = urlparse(source).netloc or source
            if source_id:
                source_ids.add(source_id.lower())

        evidence_ids = {
            item.get("evidence_id") if isinstance(item, dict) else getattr(item, "evidence_id", None)
            for item in evidence
        }
        evidence_ids.discard(None)

        corroborated = sum(1 for item in intelligence if item.get("corroboration_count", 1) >= 2)
        contradictions = sum(1 for item in intelligence if item.get("contradiction", False) or item.get("verification_status") == "conflicted")
        stale = sum(1 for item in intelligence if str(item.get("freshness_status", "")).upper() == "STALE")

        trust_values = []
        for source in source_ids:
            value = source_trust.get(source)
            if value is None:
                continue
            try:
                value = float(value)
                trust_values.append(value * 100 if 0 <= value <= 1 else value)
            except (TypeError, ValueError):
                continue

        avg_trust = round(sum(trust_values) / len(trust_values), 2) if trust_values else None
        checks = []
        if not articles:
            checks.append("no_articles")
        if not evidence_ids:
            checks.append("no_evidence")
        if len(source_ids) < 2:
            checks.append("single_source")
        if contradictions:
            checks.append("contradictory_sources")
        if stale:
            checks.append("stale_information")

        if contradictions:
            status = "needs_verification"
            action = "Re-check conflicting sources before acting."
        elif not evidence_ids or not articles:
            status = "degraded"
            action = "Collect additional primary-source evidence before acting."
        elif corroborated or len(source_ids) >= 2:
            status = "verified"
            action = "Proceed with normal confidence controls and monitor for changes."
        else:
            status = "partially_verified"
            action = "Seek an independent source before taking a high-impact action."

        confidence = 100.0
        confidence -= min(40.0, len(checks) * 12.0)
        confidence += min(20.0, corroborated * 10.0)
        if avg_trust is not None:
            confidence = confidence * 0.7 + avg_trust * 0.3
        confidence = round(max(0.0, min(100.0, confidence)), 2)

        return {
            "status": status,
            "confidence_score": confidence,
            "source_count": len(source_ids),
            "evidence_count": len(evidence_ids),
            "corroborated_count": corroborated,
            "contradiction_count": contradictions,
            "stale_count": stale,
            "average_source_trust": avg_trust,
            "checks": checks,
            "recommended_action": action,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
