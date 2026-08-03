import json
from pathlib import Path

from services.logger import get_logger

logger = get_logger(__name__)


class SourceTrustService:
    DEFAULT_TRUST_MAP = {
        "https://www.federalreserve.gov/feeds/press_all.xml": 95,
        "https://www.imf.org/external/rss/press.aspx": 88,
        "https://www.ecb.europa.eu/rss/press.html": 88,
        "https://feeds.finance.yahoo.com/rss/2.0/headline": 82,
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best": 94,
        "https://www.bloomberg.com/feeds/bbiz/sitemap_news.xml": 92,
        "https://cointelegraph.com/rss": 84,
        "https://www.coindesk.com/arc/outboundfeeds/rss/": 86,
        "https://cryptopotato.com/feed/": 72,
        "https://www.microsoft.com/en-us/research/blog/feed/": 90,
        "https://blogs.nvidia.com/feed/": 89,
        "https://blog.google/rss/": 88,
        "https://aws.amazon.com/about-aws/whats-new/recent/feed/": 90,
        "https://azure.microsoft.com/en-us/blog/feed/": 88,
        "https://cloud.google.com/blog/rss": 87,
        "https://www.cisa.gov/uscert/ncas/alerts.xml": 96,
        "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml": 95,
        "https://www.bleepingcomputer.com/feed/": 78,
        "https://github.blog/feed/": 89,
        "https://www.linuxfoundation.org/feed/": 84,
        "https://www.kubernetes.io/feed.xml": 84,
    }

    def __init__(self, path: str | None = None):
        self.path = Path(path or Path(__file__).resolve().parent.parent / "data" / "source_trust_map.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._map = self._load()

    def _load(self):
        if not self.path.exists():
            self.path.write_text(json.dumps(self.DEFAULT_TRUST_MAP, indent=2), encoding="utf-8")
            return dict(self.DEFAULT_TRUST_MAP)

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                stored = json.load(handle)
        except Exception:
            return dict(self.DEFAULT_TRUST_MAP)

        merged = dict(self.DEFAULT_TRUST_MAP)
        merged.update(stored or {})
        return merged

    def get(self, source_key: str, default: int = 60) -> int:
        if not source_key:
            return default
        return int(self._map.get(source_key, default))

    def set(self, source_key: str, trust_score: int) -> None:
        if not source_key:
            return
        self._map[source_key] = max(0, min(100, int(trust_score)))
        self._save()

    def all(self):
        return dict(self._map)

    def _save(self):
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self._map, handle, indent=2)

    def as_dict(self):
        return dict(self._map)
