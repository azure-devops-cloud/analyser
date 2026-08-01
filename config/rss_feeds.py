RSS_FEEDS = {
    "fed": [
        ("https://www.federalreserve.gov/feeds/press_all.xml", 5),
        ("https://www.imf.org/external/rss/press.aspx", 3),
        ("https://www.ecb.europa.eu/rss/press.html", 3)
    ],
    "markets": [
        ("https://feeds.finance.yahoo.com/rss/2.0/headline", 5),
        ("https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", 4),
        ("https://www.bloomberg.com/feeds/bbiz/sitemap_news.xml", 3)
    ],
    "crypto": [
        ("https://cointelegraph.com/rss", 5),
        ("https://www.coindesk.com/arc/outboundfeeds/rss/", 4),
        ("https://cryptopotato.com/feed/", 3)
    ],
    "ai": [
        ("https://www.microsoft.com/en-us/research/blog/feed/", 4),
        ("https://blogs.nvidia.com/feed/", 4),
        ("https://blog.google/rss/", 3)
    ],
    "cloud": [
        ("https://aws.amazon.com/about-aws/whats-new/recent/feed/", 4),
        ("https://azure.microsoft.com/en-us/blog/feed/", 4),
        ("https://cloud.google.com/blog/rss", 3)
    ],
    "security": [
        ("https://www.cisa.gov/uscert/ncas/alerts.xml", 5),
        ("https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml", 4),
        ("https://www.bleepingcomputer.com/feed/", 3)
    ],
    "opensource": [
        ("https://github.blog/feed/", 4),
        ("https://www.linuxfoundation.org/feed/", 3),
        ("https://www.kubernetes.io/feed.xml", 3)
    ]
}

CATEGORY_ARTICLE_CAP = 120
