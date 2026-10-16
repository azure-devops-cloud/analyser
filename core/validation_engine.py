"""Deterministic validation and confidence guardrails for agent outputs."""

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    field: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationReport:
    passed: bool
    confidence: float
    issues: tuple[ValidationIssue, ...] = ()
    evidence_coverage: float = 0.0
    corroboration: float = 0.0
    freshness: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "confidence": self.confidence,
            "issues": [asdict(issue) for issue in self.issues],
            "evidence_coverage": self.evidence_coverage,
            "corroboration": self.corroboration,
            "freshness": self.freshness,
        }


class ValidationEngine:
    """Validate evidence-backed decisions without delegating safety to an LLM."""

    def validate(self, decisions: Iterable[dict[str, Any]], evidence: Iterable[Any]) -> ValidationReport:
        decisions = list(decisions or [])
        evidence = list(evidence or [])
        issues: list[ValidationIssue] = []
        evidence_ids = {self._get(item, "evidence_id") for item in evidence}
        evidence_ids.discard(None)

        linked = 0
        for decision in decisions:
            refs = decision.get("evidence_ids") or decision.get("evidence") or []
            if isinstance(refs, dict):
                refs = refs.get("items", [])
            refs = [self._get(ref, "evidence_id") if not isinstance(ref, str) else ref for ref in refs]
            refs = [ref for ref in refs if ref]
            if refs:
                linked += 1
                missing = [ref for ref in refs if ref not in evidence_ids]
                if missing:
                    issues.append(ValidationIssue("missing_evidence", f"Unknown evidence references: {missing}", field="evidence_ids"))
            else:
                issues.append(ValidationIssue("unsupported_decision", "Decision has no evidence references", field="evidence_ids"))

            score = decision.get("score")
            if score is not None and not isinstance(score, (int, float)):
                issues.append(ValidationIssue("invalid_score", "Decision score must be numeric", field="score"))
            if score is not None and not 0 <= float(score) <= 100:
                issues.append(ValidationIssue("score_range", "Decision score must be between 0 and 100", field="score"))

        coverage = linked / len(decisions) if decisions else 1.0
        corroboration = self._corroboration(evidence)
        freshness = self._freshness(evidence)
        confidence = round(100 * (0.5 * coverage + 0.3 * corroboration + 0.2 * freshness), 2)
        passed = not any(issue.severity == "error" for issue in issues) and confidence >= 50
        return ValidationReport(passed, confidence, tuple(issues), coverage, corroboration, freshness)

    @staticmethod
    def _get(value: Any, key: str) -> Any:
        if isinstance(value, dict):
            return value.get(key)
        return getattr(value, key, None)

    def _corroboration(self, evidence: list[Any]) -> float:
        if not evidence:
            return 0.0
        sources = {self._get(item, "source") or self._get(item, "source_url") for item in evidence}
        sources.discard(None)
        return min(1.0, len(sources) / 3.0)

    def _freshness(self, evidence: list[Any]) -> float:
        if not evidence:
            return 0.0
        values = []
        for item in evidence:
            raw = self._get(item, "timestamp") or self._get(item, "published_at")
            if not raw:
                continue
            try:
                text = str(raw).replace("Z", "+00:00")
                from datetime import datetime, timezone
                age = max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(text)).total_seconds())
                values.append(max(0.0, 1.0 - age / 86400.0))
            except (TypeError, ValueError):
                continue
        return sum(values) / len(values) if values else 0.5
