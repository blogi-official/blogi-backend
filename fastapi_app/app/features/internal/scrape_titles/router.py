import traceback

from fastapi import APIRouter, HTTPException

from app.features.internal.scrape_titles.schemas import ScrapeResponse
from app.features.internal.scrape_titles.services import \
    fetch_and_send_to_django

scrape_title_router = APIRouter(prefix="/scrape", tags=["Scraper"])


@scrape_title_router.get("/titles", response_model=ScrapeResponse)
async def scrape_titles_endpoint():
    try:
        result = await fetch_and_send_to_django()
        return {"data": result}

    except Exception as e:
        print("[ERROR]", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="네이버 페이지 파싱 중 오류가 발생했습니다."
        )
