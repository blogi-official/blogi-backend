import asyncio

import httpx

from app.core.config import settings
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.scraper.news_scraper import (
    extract_news_content,
)


async def fetch_keyword_from_django() -> dict | None:
    url = f"{settings.django_api_url}/api/internal/target-keyword"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"[ERROR] Django에서 keyword 받아오기 실패: {e}")
    return None


async def test_scrape_real_keyword():
    keyword_data = await fetch_keyword_from_django()
    if not keyword_data:
        print("[FAIL] 키워드 받아오기 실패")
        return

    title = keyword_data["title"]
    print(f"[TEST] 저장된 키워드로 뉴스 검색 시작 → '{title}'")

    results = await search_news(query=title, type="news", display=1)
    if not results:
        print("[FAIL] 검색 결과 없음.")
        return

    item = results[0]
    origin_link = item.get("link")
    if not origin_link:
        print("[FAIL] 링크 없음.")
        return

    print(f"[INFO] 기사 링크: {origin_link}")
    content = await extract_news_content(origin_link)

    if content and len(content.strip()) > 0:
        print(f"[SUCCESS] 본문 추출 성공 (길이: {len(content)}자)")
        print("본문 미리보기:\n")
        preview = content[:500].replace("\n", " ").replace("\r", "")
        print(preview if preview else "(본문 있음 - 미리보기 생략됨)")
    else:
        print("[FAIL] 본문 추출 실패 또는 내용 없음")


if __name__ == "__main__":
    asyncio.run(test_scrape_real_keyword())
