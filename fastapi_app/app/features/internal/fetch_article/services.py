from urllib.parse import urlparse

from app.common.constants.category import CATEGORY_META_MAP
from app.common.logger import get_logger
from app.features.internal.django_client import (
    deactivate_keyword,
    fetch_keywords_from_django,
    send_articles_to_django,
)
from app.features.internal.fetch_article.smart_blog_fetcher import (
    fetch_smart_article as fetch_smart_blog,
)
from app.features.internal.fetch_article.smart_news_fetcher import fetch_smart_article

logger = get_logger(__name__)


async def scrape_and_send_articles():
    while True:
        raw_response = await fetch_keywords_from_django()
        keyword = raw_response.get("data")

        logger.info(f"fetch_keywords_from_django 결과: {keyword}")

        # 키워드 없으면 루프 종료
        if not keyword or not isinstance(keyword, dict):
            logger.info("더 이상 수집할 키워드가 없습니다. 종료합니다.")
            break

        title = keyword.get("title")
        keyword_id = keyword.get("id")
        category = keyword.get("category")

        # 필수값 누락 시 비활성화 및 continue
        if not title or not keyword_id or not category:
            logger.warning(f"[SKIP] 필수 정보 누락: {keyword}")
            await deactivate_keyword(keyword_id)
            continue

        category_info = CATEGORY_META_MAP.get(category)
        if not category_info:
            logger.warning(f"[SKIP] 알 수 없는 카테고리: {category}")
            await deactivate_keyword(keyword_id)
            continue

        search_type = category_info["type"]
        logger.info(f"[PROCESS] keyword_id={keyword_id}, title={title}, type={search_type}")

        try:
            # 블로그 vs 뉴스 처리
            if search_type == "news":
                article = await fetch_smart_article(keyword_id, title)
            else:
                article = await fetch_smart_blog(keyword_id, title)

            if article is None:
                logger.info(f"[FAIL] 수집 실패: keyword_id={keyword_id}, title={title}")
                await deactivate_keyword(keyword_id)
                continue

            if not isinstance(article, dict):
                logger.warning(f"[FAIL] 결과 형식 오류: keyword_id={keyword_id}, article={article}")
                await deactivate_keyword(keyword_id)
                continue

            logger.info(f"[SUCCESS] 수집 완료: keyword_id={keyword_id}, title={article['title']}")
            result = await send_articles_to_django([article])
            logger.info(f"[SEND] Django 저장 결과: {result}")

        except Exception as e:
            logger.error(
                f"[ERROR] 처리 중 예외 발생: keyword_id={keyword_id}, title={title} - {e}",
                exc_info=True,
            )
            await deactivate_keyword(keyword_id)
            continue
