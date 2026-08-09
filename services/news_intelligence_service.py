from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
import hashlib
import re


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    published: str = ""
    source: str = ""
    category: str = "general"
    source_trust: float = 0.5
    importance: float = 0.0
    freshness: float = 0.0
    actionability: float = 0.0
    score: float = 0.0
    impact: str = "LOW"
    why_it_matters: str = ""
    actions: tuple[str, ...] = field(default_factory=tuple)
    evidence_id: str = ""
    affected_assets: tuple[str, ...] = field(default_factory=tuple)
    corroboration_count: int = 1
    corroborating_sources: tuple[str, ...] = field(default_factory=tuple)
    contradiction_detected: bool = False
    temporal_status: str = "CURRENT"

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title, "link": self.link, "published": self.published,
            "source": self.source, "category": self.category, "source_trust": self.source_trust,
            "importance": self.importance, "freshness": self.freshness, "actionability": self.actionability,
            "score": self.score, "impact": self.impact, "why_it_matters": self.why_it_matters,
            "actions": list(self.actions), "evidence_id": self.evidence_id,
            "affected_assets": list(self.affected_assets), "corroboration_count": self.corroboration_count,
            "corroborating_sources": list(self.corroborating_sources),
            "contradiction_detected": self.contradiction_detected, "temporal_status": self.temporal_status,
        }


class NewsIntelligenceService:
    """Turn noisy news feeds into ranked, evidence-backed actionable intelligence."""

    HIGH_IMPACT_TERMS = {
        "rate", "fed", "fomc", "inflation", "cpi", "jobs", "payroll", "recession",
        "sanction", "war", "tariff", "default", "hack", "breach", "outage", "regulation",
        "etf", "approval", "ban", "acquisition", "earnings", "guidance",
    }
    ACTION_TERMS = {
        "raises", "cuts", "falls", "rises", "approved", "rejected", "launches", "warns",
        "halts", "resumes", "reports", "beats", "misses", "plans", "announces",
    }
    POSITIVE_TERMS = {"rises", "raises", "approved", "beats", "growth", "bullish", "boosts", "gains"}
    NEGATIVE_TERMS = {"falls", "cuts", "rejected", "misses", "decline", "bearish", "loss", "drops"}

    def __init__(self, fetcher: Callable[..., list[dict[str, Any]]] | None = None, llm_client=None):
        self.fetcher = fetcher
        self.llm_client = llm_client

    @staticmethod
    def _clean(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @staticmethod
    def _fingerprint(item: dict[str, Any]) -> str:
        raw = "|".join([
            NewsIntelligenceService._clean(item.get("title")).lower(),
            NewsIntelligenceService._clean(item.get("link")).lower(),
        ])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _story_key(title: str) -> str:
        words = re.findall(r"[a-z0-9]+", title.lower())
        stop = {
            "the", "a", "an", "to", "of", "in", "on", "for", "and", "with", "says", "said",
            "after", "before", "decision", "report", "reports", "source", "officially",
            "rises", "raises", "approved", "beats", "growth", "bullish", "boosts", "gains",
            "falls", "cuts", "rejected", "misses", "decline", "bearish", "loss", "drops",
        }
        return " ".join(word for word in words if word not in stop)[:180]

    @staticmethod
    def _freshness(published: str, now: datetime | None = None) -> float:
        if not published:
            return 0.25
        try:
            parsed = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            current = now or datetime.now(timezone.utc)
            age_hours = (current - parsed).total_seconds() / 3600
            if age_hours < -1:
                return 0.0
            return round(max(0.0, min(1.0, 1.0 - max(0.0, age_hours) / 168.0)), 3)
        except (TypeError, ValueError):
            return 0.25

    @staticmethod
    def _temporal_status(published: str, freshness: float) -> str:
        if not published:
            return "UNKNOWN"
        if freshness <= 0.05:
            return "STALE"
        return "CURRENT"

    def _score(self, item: dict[str, Any], trust: float, now: datetime | None = None, corroboration: int = 1, contradiction: bool = False) -> tuple[float, float, float]:
        title = self._clean(item.get("title"))
        words = set(re.findall(r"[a-z0-9]+", title.lower()))
        impact_hits = len(words & self.HIGH_IMPACT_TERMS)
        action_hits = len(words & self.ACTION_TERMS)
        freshness = self._freshness(self._clean(item.get("published")), now)
        corroboration_bonus = min(0.15, max(0, corroboration - 1) * 0.05)
        contradiction_penalty = 0.15 if contradiction else 0.0
        importance = min(1.0, max(0.0, 0.45 * trust + 0.30 * min(1.0, impact_hits / 2) + 0.25 * freshness + corroboration_bonus - contradiction_penalty))
        actionability = min(1.0, max(0.0, 0.55 * min(1.0, action_hits / 2) + 0.25 * min(1.0, impact_hits / 2) + 0.20 * trust + corroboration_bonus - contradiction_penalty))
        return round(importance, 3), round(freshness, 3), round(actionability, 3)

    def _why(self, item: dict[str, Any], impact: str, corroboration: int, contradiction: bool) -> str:
        title = self._clean(item.get("title")) or "This development"
        verification = " Multiple sources corroborate the development." if corroboration > 1 else " Independent confirmation is limited."
        warning = " Conflicting coverage was detected, so treat the conclusion cautiously." if contradiction else ""
        if impact == "HIGH":
            return f"{title}. This may affect market expectations, risk, or near-term positioning.{verification}{warning}"
        if impact == "MEDIUM":
            return f"{title}. Monitor for confirmation or follow-through before acting.{verification}{warning}"
        return f"{title}. Useful context, but not enough on its own for a trading decision.{verification}{warning}"

    def _actions(self, impact: str, category: str, corroboration: int, contradiction: bool) -> tuple[str, ...]:
        if contradiction:
            return ("Verify the conflicting primary sources", "Do not act until the discrepancy is resolved", "Monitor for an authoritative update")
        if impact == "HIGH":
            return ("Verify the primary source", "Check the affected asset or sector", "Wait for price confirmation before acting")
        if category in {"security", "cloud", "ai", "opensource"}:
            return ("Open the source for implementation details", "Check whether the change affects your stack")
        if corroboration > 1:
            return ("Check the corroborating sources", "Compare with current market positioning")
        return ("Monitor for confirmation", "Compare with current market positioning")

    @staticmethod
    def _affected_assets(item: dict[str, Any]) -> tuple[str, ...]:
        raw = item.get("affected_assets", item.get("assets", item.get("asset")))
        if isinstance(raw, str):
            values = [raw]
        elif isinstance(raw, (list, tuple, set)):
            values = list(raw)
        else:
            values = []
        cleaned = []
        for value in values:
            value = str(value).strip().upper()
            if value and value not in cleaned:
                cleaned.append(value)
        return tuple(cleaned[:5])

    def _enrich_with_llm(self, result: dict[str, Any]) -> dict[str, Any]:
        if not self.llm_client:
            return result
        try:
            enriched = self.llm_client(result)
            if not isinstance(enriched, dict):
                return result
            result["why_it_matters"] = self._clean(enriched.get("why_it_matters")) or result["why_it_matters"]
            supplied = enriched.get("actions")
            if isinstance(supplied, list):
                actions = [self._clean(x) for x in supplied if self._clean(x)]
                if actions:
                    result["actions"] = actions[:3]
        except Exception:
            pass
        return result

    @staticmethod
    def _quality_groups(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            groups.setdefault(NewsIntelligenceService._story_key(item["title"]), []).append(item)
        return groups

    def analyze(self, articles: Iterable[dict[str, Any]], source_trust: dict[str, float] | None = None, now: datetime | None = None) -> list[dict[str, Any]]:
        source_trust = source_trust or {}
        unique: dict[str, dict[str, Any]] = {}
        for raw in articles or []:
            if not isinstance(raw, dict):
                continue
            title = self._clean(raw.get("title"))
            link = self._clean(raw.get("link"))
            if not title or not link:
                continue
            item = dict(raw)
            item["title"], item["link"] = title, link
            unique.setdefault(self._fingerprint(item), item)

        raw_items = list(unique.values())
        groups = self._quality_groups(raw_items)
        output: list[dict[str, Any]] = []
        for item in raw_items:
            source = self._clean(item.get("source")) or self._clean(item.get("link"))
            trust = float(source_trust.get(source, item.get("source_trust", 0.5)) or 0.5)
            trust = max(0.0, min(1.0, trust))
            group = groups.get(self._story_key(item["title"]), [item])
            sources = tuple(dict.fromkeys(self._clean(other.get("source")) or self._clean(other.get("link")) for other in group))
            title_words = set(re.findall(r"[a-z0-9]+", item["title"].lower()))
            has_positive = bool(title_words & self.POSITIVE_TERMS)
            has_negative = bool(title_words & self.NEGATIVE_TERMS)
            group_positive = any(bool(set(re.findall(r"[a-z0-9]+", other["title"].lower())) & self.POSITIVE_TERMS) for other in group)
            group_negative = any(bool(set(re.findall(r"[a-z0-9]+", other["title"].lower())) & self.NEGATIVE_TERMS) for other in group)
            contradiction = group_positive and group_negative and (has_positive or has_negative)
            freshness = self._freshness(self._clean(item.get("published")), now)
            temporal_status = self._temporal_status(self._clean(item.get("published")), freshness)
            importance, freshness, actionability = self._score(item, trust, now, len(group), contradiction)
            score = round((0.50 * importance + 0.30 * actionability + 0.20 * freshness) * 100, 1)
            if temporal_status == "STALE":
                score = min(score, 39.9)
            impact = "HIGH" if score >= 70 else "MEDIUM" if score >= 45 else "LOW"
            category = self._clean(item.get("category")) or "general"
            evidence_id = f"news-{self._fingerprint(item)}"
            result = NewsItem(
                title=item["title"], link=item["link"], published=self._clean(item.get("published")), source=source,
                category=category, source_trust=trust, importance=importance, freshness=freshness,
                actionability=actionability, score=score, impact=impact,
                why_it_matters=self._why(item, impact, len(group), contradiction),
                actions=self._actions(impact, category, len(group), contradiction), evidence_id=evidence_id,
                affected_assets=self._affected_assets(item), corroboration_count=len(group),
                corroborating_sources=sources, contradiction_detected=contradiction, temporal_status=temporal_status,
            ).as_dict()
            output.append(self._enrich_with_llm(result))

        output.sort(key=lambda x: (x["importance"], x["actionability"], x["freshness"]), reverse=True)
        return output
