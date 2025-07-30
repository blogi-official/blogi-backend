# naver_api.py
import asyncio

import httpx

from app.core.config import settings

async def search_news(query: str, display: int = 1):
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {"query": query, "display": display, "sort": "date"}
    headers = {
        "X-Naver-Client-Id": settings.naver_client_id,
        "X-Naver-Client-Secret": settings.naver_client_secret,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"네이버 뉴스 검색 실패, status_code={response.status_code}")

            data = response.json()
            return data.get("items", [])
    except asyncio.CancelledError:
        # 작업이 취소되었을 때 적절히 처리 (로그 남기기 등)
        print(f"search_news 작업이 취소되었습니다. query={query}")
        raise  # 반드시 다시 raise 해야 정상 종료됨
    except Exception as e:
        print(f"search_news 에러 발생: {e}")
        raise
