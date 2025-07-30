from fastapi import APIRouter

from app.features.internal.fetch_article.router import fetch_article_router
from app.features.internal.scrape_titles.router import scrape_title_router

internal_router = APIRouter(prefix="/internal")

# internal_router.include_router(scrape_title_router)
internal_router.include_router(fetch_article_router)
