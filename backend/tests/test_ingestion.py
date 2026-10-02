from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.ingestion import service
from app.models import Article, Category, Source

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Example Security</title>
    <link>https://example.com</link>
    <description>Security feed</description>
    <item>
      <title>Ransomware exploits critical CVE-2026-1234</title>
      <link>https://example.com/story?utm_source=test</link>
      <description><![CDATA[<p>A malware campaign is exploiting a security flaw.</p>]]></description>
      <pubDate>Thu, 01 Oct 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@pytest.mark.asyncio
async def test_ingestion_is_idempotent(monkeypatch, session):
    source = Source(
        name="Example Security",
        slug="example-security",
        feed_url="https://example.com/feed.xml",
        site_url="https://example.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    categories = [
        Category(name="Ransomware", slug="ransomware"),
        Category(name="Vulnerability", slug="vulnerability"),
        Category(name="Malware", slug="malware"),
        Category(name="Threat Intelligence", slug="threat-intelligence"),
    ]
    session.add_all([source, *categories])
    await session.commit()

    async def fake_fetch(client, url):
        return RSS

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch)

    first = await service.ingest_source(session, source)
    second = await service.ingest_source(session, source)

    total = await session.scalar(select(func.count(Article.id)))
    assert first.inserted == 1
    assert second.inserted == 0
    assert second.skipped == 1
    assert total == 1

    article = (await session.execute(select(Article))).scalar_one()
    assert article.canonical_url == "https://example.com/story"
