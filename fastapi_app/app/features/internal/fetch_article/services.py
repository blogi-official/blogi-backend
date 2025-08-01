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
    raw_response = await fetch_keywords_from_django()
    keyword = raw_response.get("data")

    logger.info(f"fetch_keywords_from_django 결과: {keyword}")

    # 유효성 검증
    if not keyword or not isinstance(keyword, dict):
        logger.info("유효한 키워드가 없습니다.")
        return {"message": "키워드가 존재하지 않습니다."}

    title = keyword.get("title")
    keyword_id = keyword.get("id")
    category = keyword.get("category")

    if not title or not keyword_id or not category:
        logger.warning(f"키워드 데이터 누락 또는 카테고리 없음: {keyword}")
        await deactivate_keyword(keyword_id)
        return {"message": "키워드 정보 누락"}

    category_info = CATEGORY_META_MAP.get(category)
    if not category_info:
        logger.warning(f"알 수 없는 카테고리: {category}")
        await deactivate_keyword(keyword_id)
        return {"message": "알 수 없는 카테고리"}

    search_type = category_info["type"]
    logger.info(f"[PROCESS] keyword_id={keyword_id}, title={title}, type={search_type}")

    try:
        if search_type == "news":
            article = await fetch_smart_article(keyword_id, title)
        else:
            article = await fetch_smart_blog(keyword_id, title)

        # None 또는 잘못된 형식 처리
        if article is None:
            logger.info(f"[FAIL] 스마트 수집 실패: keyword_id={keyword_id}, title={title}")
            await deactivate_keyword(keyword_id)
            return {"message": "수집 실패"}
        if not isinstance(article, dict):
            logger.warning(f"[FAIL] 수집 결과 형식 오류: keyword_id={keyword_id}, article={article}")
            await deactivate_keyword(keyword_id)
            return {"message": "수집 결과 형식 오류"}

        logger.info(f"[SUCCESS] 수집 완료: keyword_id={keyword_id}, title={article['title']}")
        result = await send_articles_to_django([article])
        logger.info(f"[SEND] Django 저장 결과: {result}")
        return result

    except Exception as e:
        logger.error(f"[ERROR] '{title}' 처리 중 에러: {e}", exc_info=True)
        await deactivate_keyword(keyword_id)
        return {"message": "처리 중 에러 발생"}
