import asyncio
from unittest.mock import patch

from app.common.logger import setup_logger
from app.features.internal.fetch_article.services import scrape_and_send_articles

setup_logger()

TEST_KEYWORD_ID = 104  # Django DB에 존재해야 함


async def run_test():
    print(f"\n🔍 테스트 시작: keyword_id={TEST_KEYWORD_ID}")
    print("➡ 수집 시도 (실패 유도: fetch_smart_article이 None 반환)")

    # ✅ fetch_keywords_from_django는 정상 카테고리("경제")를 반환
    async def mock_fetch_keywords_from_django():
        return {
            "data": {
                "id": TEST_KEYWORD_ID,
                "title": "실패유도테스트_스크랩핑",
                "category": "경제",  # ✅ CATEGORY_META_MAP에 있음
            }
        }

    # ✅ 스마트 뉴스 수집 실패 유도 (None 리턴)
    async def mock_fetch_smart_article(keyword_id: int, title: str):
        return None

    # ✅ patch 두 개 동시에 적용
    with (
        patch(
            "app.features.internal.fetch_article.services.fetch_keywords_from_django",
            new=mock_fetch_keywords_from_django,
        ),
        patch(
            "app.features.internal.fetch_article.services.fetch_smart_article",
            new=mock_fetch_smart_article,
        ),
    ):
        result = await scrape_and_send_articles()

    print("\n📦 결과:", result)
    print(
        f"✅ 확인: Django Admin 또는 DB에서 keyword_id={TEST_KEYWORD_ID} 의 is_active=False 로 변경되었는지 확인해주세요."
    )


if __name__ == "__main__":
    asyncio.run(run_test())
