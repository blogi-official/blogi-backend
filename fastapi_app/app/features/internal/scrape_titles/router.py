import traceback

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.features.internal.scrape_titles.services import fetch_and_send_to_django

scrape_title_router = APIRouter(prefix="/scrape", tags=["Keyword - Scraper"])
api_key_header = APIKeyHeader(name="x-internal-secret", auto_error=True)


# 숏텐츠 제목(키워드) 스크랩
@scrape_title_router.get("/titles")
async def scrape_titles(x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    try:
        result = await fetch_and_send_to_django()
        return result

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="네이버 페이지 파싱 중 오류가 발생했습니다.")
