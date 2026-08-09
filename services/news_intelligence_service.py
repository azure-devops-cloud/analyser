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
    impact: str = "LOW"
    why_it_matters: str = ""
    actions: tuple[str, ...] = field(default_factory=tuple)
    evidence_id: str = ""
    affected_assets: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published,
            "source": self.source,
            "category": self.category,
            "source_trust": self.source_trust,
            "importance": self.importance,
            "freshness": self.freshness,
            "actionability": self.actionability,
            "impact": self.impact,
            "why_it_matters": self.why_it_matters,
            "actions": list(self.actions),
            "evidence_id": self.evidence_id,
            "affected_assets": list(self.affected_assets),
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
    def _freshness(published: str, now: datetime | None = None) -> float:
        if not published:
            return 0.25
        try:
            parsed = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            current = now or datetime.now(timezone.utc)
            hours = max(0.0, (current - parsed).total_seconds() / 3600)
            return round(max(0.0, min(1.0, 1.0 - hours / 168.0)), 3)
        except (TypeError, ValueError):
            return 0.25

    def _score(self, item: dict[str, Any], trust: float, now: datetime | None = None) -> tuple[float, float, float]:
        title = self._clean(item.get("title"))
        words = set(re.findall(r"[a-z0-9]+", title.lower()))
        impact_hits = len(words & self.HIGH_IMPACT_TERMS)
        action_hits = len(words & self.ACTION_TERMS)
        freshness = self._freshness(self._clean(item.get("published")), now)
        importance = min(1.0, 0.45 * trust + 0.30 * min(1.0, impact_hits / 2) + 0.25 * freshness)
        actionability = min(1.0, 0.55 * min(1.0, action_hits / 2) + 0.25 * min(1.0, impact_hits / 2) + 0.20 * trust)
        return round(importance, 3), round(freshness, 3), round(actionability, 3)

    def _why(self, item: dict[str, Any], impact: str) -> str:
        title = self._clean(item.get("title")) or "This development"
        if impact == "HIGH":
            return f"{title}. This may affect market expectations, risk, or near-term positioning."
        if impact == "MEDIUM":
            return f"{title}. Monitor for confirmation or follow-through before acting."
        return f"{title}. Useful context, but not enough on its own for a trading decision."

    def _actions(self, impact: str, category: str) -> tuple[str, ...]:
        if impact == "HIGH":
            return ("Verify the primary source", "Check the affected asset or sector", "Wait for price confirmation before acting")
        if category in {"security", "cloud", "ai", "opensource"}:
            return ("Open the source for implementation details", "Check whether the change affects your stack")
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

        output: list[dict[str, Any]] = []
        for item in unique.values():
            source = self._clean(item.get("source")) or self._clean(item.get("link"))
            trust = float(source_trust.get(source, item.get("source_trust", 0.5)) or 0.5)
            trust = max(0.0, min(1.0, trust))
            importance, freshness, actionability = self._score(item, trust, now)
            score = round((0.50 * importance + 0.30 * actionability + 0.20 * freshness) * 100, 1)
            impact = "HIGH" if score >= 70 else "MEDIUM" if score >= 45 else "LOW"
            category = self._clean(item.get("category")) or "general"
            evidence_id = f"news-{self._fingerprint(item)}"
            result = NewsItem(
                title=self._clean(item.get("title")),
                link=self._clean(item.get("link")),
                published=self._clean(item.get("published")),
                source=source,
                category=category,
                source_trust=trust,
                importance=importance,
                freshness=freshness,
                actionability=actionability,
                impact=impact,
                why_it_matters=self._why(item, impact),
                actions=self._actions(impact, category),
                evidence_id=evidence_id,
                affected_assets=self._affected_assets(item),
            ).as_dict()
            output.append(self._enrich_with_llm(result))

        output.sort(key=lambda x: (x["importance"], x["actionability"], x["freshness"]), reverse=True)
        return output
