import traceback

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.features.internal.fetch_article.services import scrape_and_send_articles
from app.features.internal.scrape_titles.services import fetch_and_send_to_django

fetch_article_router = APIRouter(prefix="/fetch", tags=["Article - Scraper"])
api_key_header = APIKeyHeader(name="x-internal-secret", auto_error=True)


# 기사 본문 스크랩
@fetch_article_router.get("/article/")
async def get_article(x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    try:
        result = await scrape_and_send_articles()
        return result

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="네이버 페이지 파싱 중 오류가 발생했습니다.")
