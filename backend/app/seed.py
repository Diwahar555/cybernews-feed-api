from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.ingestion.catalog import DEFAULT_CATEGORIES, DEFAULT_SOURCES
from app.models import Category, Source


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for name, slug in DEFAULT_CATEGORIES:
            if not await db.scalar(select(Category.id).where(Category.slug == slug)):
                db.add(Category(name=name, slug=slug))

        for item in DEFAULT_SOURCES:
            existing = await db.scalar(select(Source).where(Source.slug == item["slug"]))
            if existing is None:
                db.add(Source(**item, is_active=True, created_at=datetime.now(timezone.utc)))
            else:
                existing.name = item["name"]
                existing.feed_url = item["feed_url"]
                existing.site_url = item["site_url"]

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
