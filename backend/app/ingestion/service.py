from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.ingestion.classifier import classify
from app.ingestion.utils import (
    canonicalize_url,
    clean_text,
    entry_datetime,
    extract_image_url,
    make_content_hash,
)
from app.models import Article, Category, Source

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    source: str
    fetched: int = 0
    inserted: int = 0
    skipped: int = 0
    error: str | None = None


def _is_retryable_fetch_error(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(_is_retryable_fetch_error),
    reraise=True,
)
async def _fetch_feed(client: httpx.AsyncClient, url: str) -> bytes:
    response = await client.get(url)
    response.raise_for_status()
    return response.content


async def _category_map(db: AsyncSession) -> dict[str, Category]:
    rows = (await db.execute(select(Category))).scalars().all()
    return {row.slug: row for row in rows}


async def ingest_source(db: AsyncSession, source: Source) -> IngestionResult:
    source_slug = source.slug
    result = IngestionResult(source=source_slug)
    source_id = source.id
    headers = {
        "User-Agent": settings.ingestion_user_agent,
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
    }
    try:
        async with httpx.AsyncClient(
            timeout=settings.ingestion_http_timeout_seconds,
            follow_redirects=True,
            headers=headers,
        ) as client:
            payload = await _fetch_feed(client, source.feed_url)

        feed = feedparser.parse(payload)
        if getattr(feed, "bozo", False) and not feed.entries:
            raise ValueError(f"Invalid or empty feed: {getattr(feed, 'bozo_exception', 'unknown error')}")

        categories = await _category_map(db)
        now = datetime.now(timezone.utc)
        entries = feed.entries[: settings.ingestion_max_entries_per_source]
        result.fetched = len(entries)

        for entry in entries:
            title = clean_text(entry.get("title"), 500)
            raw_url = entry.get("link")
            if not title or not raw_url:
                result.skipped += 1
                continue

            try:
                canonical_url = canonicalize_url(raw_url)
            except ValueError:
                result.skipped += 1
                continue
            published_at = entry_datetime(entry)
            content_hash = make_content_hash(title, source_slug, published_at, canonical_url)

            exists = await db.scalar(
                select(Article.id).where(
                    (Article.canonical_url == canonical_url) | (Article.content_hash == content_hash)
                )
            )
            if exists:
                result.skipped += 1
                continue

            summary = clean_text(entry.get("summary") or entry.get("description"), 1200)
            category_slugs = classify(title, summary)
            article = Article(
                source_id=source_id,
                title=title,
                url=raw_url,
                canonical_url=canonical_url,
                summary=summary,
                author=clean_text(entry.get("author"), 250),
                image_url=extract_image_url(entry),
                content_hash=content_hash,
                published_at=published_at,
                fetched_at=now,
                language="en",
                categories=[categories[slug] for slug in category_slugs if slug in categories],
            )
            try:
                async with db.begin_nested():
                    db.add(article)
                    await db.flush()
                result.inserted += 1
            except IntegrityError:
                # A concurrent worker may have inserted the same canonical URL after our
                # existence check. The nested transaction rolls back only this article.
                result.skipped += 1

        source.last_success_at = now
        source.last_error = None
        await db.commit()
        logger.info(
            "ingestion source=%s fetched=%s inserted=%s skipped=%s",
            source_slug,
            result.fetched,
            result.inserted,
            result.skipped,
        )
    except Exception as exc:
        await db.rollback()
        persisted_source = await db.get(Source, source_id)
        if persisted_source is not None:
            persisted_source.last_error = str(exc)[:2000]
            await db.commit()
        result.error = str(exc)
        logger.exception("ingestion failed source=%s", source_slug)
    return result


async def ingest_all(db: AsyncSession) -> list[IngestionResult]:
    sources = (
        await db.execute(select(Source).where(Source.is_active.is_(True)).order_by(Source.id))
    ).scalars().all()
    results = []
    for source in sources:
        results.append(await ingest_source(db, source))
    return results
