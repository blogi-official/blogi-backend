import httpx

from app.features.internal.scrape_titles.config import DJANGO_API_ENDPOINT
from app.features.internal.scrape_titles.naver_scraper import scrape_titles


async def fetch_and_send_to_django():
    try:
        print("[DEBUG] scrape_titles() 시작")
        keywords = await scrape_titles()
        print(f"[DEBUG] scrape_titles() 결과: {len(keywords)}개 수집")
        if not keywords:
            return {
                "message": "수집된 키워드가 없습니다.",
                "created_count": 0,
                "skipped_count": 0,
            }

        async with httpx.AsyncClient() as client:
            res = await client.post(DJANGO_API_ENDPOINT, json=keywords)
            res.raise_for_status()
            return res.json()

    except Exception as e:
        raise RuntimeError("네이버 페이지 파싱 중 오류가 발생했습니다.") from e
