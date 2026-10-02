from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    site_url: str | None = None


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    canonical_url: str
    summary: str | None
    author: str | None
    image_url: str | None
    published_at: datetime | None
    fetched_at: datetime
    source: SourceBrief
    categories: list[CategoryBrief] = Field(default_factory=list)


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class ArticlePage(BaseModel):
    items: list[ArticleOut]
    meta: PaginationMeta
