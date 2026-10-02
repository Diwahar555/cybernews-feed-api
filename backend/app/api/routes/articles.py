from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.article import ArticleOut, ArticlePage, PaginationMeta
from app.services.articles import get_article, list_articles

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticlePage)
async def articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: str | None = Query(None, max_length=120),
    category: str | None = Query(None, max_length=80),
    search: str | None = Query(None, min_length=2, max_length=200),
    db: AsyncSession = Depends(get_db),
) -> ArticlePage:
    items, total, pages = await list_articles(
        db,
        page=page,
        page_size=page_size,
        source=source,
        category=category,
        search=search,
    )
    return ArticlePage(
        items=[ArticleOut.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
    )


@router.get("/{article_id}", response_model=ArticleOut)
async def article_detail(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ArticleOut:
    article = await get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return ArticleOut.model_validate(article)
