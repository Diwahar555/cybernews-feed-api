from __future__ import annotations

import math
import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Article, Category, Source


async def list_articles(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    source: str | None = None,
    category: str | None = None,
    search: str | None = None,
):
    filters = []
    stmt: Select = select(Article).options(
        selectinload(Article.categories),
    )

    if source:
        stmt = stmt.join(Article.source)
        filters.append(Source.slug == source)

    if category:
        stmt = stmt.join(Article.categories)
        filters.append(Category.slug == category)

    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Article.title).like(term),
                func.lower(func.coalesce(Article.summary, "")).like(term),
            )
        )

    if filters:
        stmt = stmt.where(*filters)

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = int((await db.execute(count_stmt)).scalar_one())

    stmt = (
        stmt.order_by(Article.published_at.desc().nullslast(), Article.fetched_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list((await db.execute(stmt)).unique().scalars().all())
    pages = math.ceil(total / page_size) if total else 0
    return items, total, pages


async def get_article(db: AsyncSession, article_id: uuid.UUID) -> Article | None:
    stmt = (
        select(Article)
        .options(selectinload(Article.categories))
        .where(Article.id == article_id)
    )
    return (await db.execute(stmt)).unique().scalar_one_or_none()
