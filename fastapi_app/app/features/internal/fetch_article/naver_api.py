# naver_api.py
import httpx
import os

from app.core.config import settings

headers = {
    "X-Naver-Client-Id": settings.naver_client_id,
    "X-Naver-Client-Secret": settings.naver_client_secret,
}

async def search_news(query: str):
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {"query": query, "display": 5, "sort": "date"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception("네이버 뉴스 검색 실패")

        data = response.json()
        return data.get("items", [])
