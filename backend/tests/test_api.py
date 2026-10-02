from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article, Category, Source


async def seed_rows(session: AsyncSession):
    source = Source(
        name="Example Security",
        slug="example-security",
        feed_url="https://example.com/feed.xml",
        site_url="https://example.com",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    vuln = Category(name="Vulnerability", slug="vulnerability")
    malware = Category(name="Malware", slug="malware")
    session.add_all([source, vuln, malware])
    await session.flush()

    article = Article(
        source_id=source.id,
        title="Critical browser vulnerability patched",
        url="https://example.com/browser-vuln",
        canonical_url="https://example.com/browser-vuln",
        summary="A remote code execution flaw has been fixed.",
        author="Security Desk",
        image_url=None,
        content_hash="a" * 64,
        published_at=datetime.now(timezone.utc),
        fetched_at=datetime.now(timezone.utc),
        categories=[vuln],
        language="en",
    )
    session.add(article)
    await session.commit()
    return article


@pytest.mark.asyncio
async def test_liveness(client):
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_article_search_and_filters(client, session):
    await seed_rows(session)
    response = await client.get(
        "/api/v1/articles",
        params={"search": "browser", "source": "example-security", "category": "vulnerability"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 1
    assert payload["items"][0]["title"] == "Critical browser vulnerability patched"
    assert payload["items"][0]["source"]["slug"] == "example-security"


@pytest.mark.asyncio
async def test_article_detail_404(client):
    response = await client.get("/api/v1/articles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
