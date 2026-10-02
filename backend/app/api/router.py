from fastapi import APIRouter

from app.api.routes.articles import router as articles_router
from app.api.routes.categories import router as categories_router
from app.api.routes.health import router as health_router
from app.api.routes.sources import router as sources_router

api_router = APIRouter()
api_router.include_router(articles_router)
api_router.include_router(sources_router)
api_router.include_router(categories_router)
api_router.include_router(health_router)
