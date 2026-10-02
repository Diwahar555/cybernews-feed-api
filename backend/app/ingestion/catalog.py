from __future__ import annotations

DEFAULT_SOURCES = [
    {
        "name": "The Hacker News",
        "slug": "the-hacker-news",
        "feed_url": "https://feeds.feedburner.com/TheHackersNews",
        "site_url": "https://thehackernews.com/",
    },
    {
        "name": "BleepingComputer",
        "slug": "bleepingcomputer",
        "feed_url": "https://www.bleepingcomputer.com/feed/",
        "site_url": "https://www.bleepingcomputer.com/",
    },
    {
        "name": "Krebs on Security",
        "slug": "krebs-on-security",
        "feed_url": "https://krebsonsecurity.com/feed/",
        "site_url": "https://krebsonsecurity.com/",
    },
    {
        "name": "SecurityWeek",
        "slug": "securityweek",
        "feed_url": "https://www.securityweek.com/feed/",
        "site_url": "https://www.securityweek.com/",
    },
    {
        "name": "Schneier on Security",
        "slug": "schneier-on-security",
        "feed_url": "https://www.schneier.com/feed/atom/",
        "site_url": "https://www.schneier.com/",
    },
]

DEFAULT_CATEGORIES = [
    ("General Security", "general-security"),
    ("Ransomware", "ransomware"),
    ("Data Breach", "data-breach"),
    ("Vulnerability", "vulnerability"),
    ("Malware", "malware"),
    ("Phishing", "phishing"),
    ("Cloud Security", "cloud-security"),
    ("Supply Chain", "supply-chain"),
    ("Threat Intelligence", "threat-intelligence"),
    ("Privacy", "privacy"),
]
