from fastapi import APIRouter

from app.features.internal.scrape_titles.router import scrape_title_router

internal_router = APIRouter(prefix="/internal")

internal_router.include_router(scrape_title_router)