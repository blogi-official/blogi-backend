from app.common.logger import get_logger
from app.common.http_client import send_articles_to_django  # 본문 전송용 공통 함수
from app.core.config import settings
import httpx

from app.features.internal.djnago_client import fetch_keywords_from_django
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.naver_scraper import extract_article_content

logger = get_logger(__name__)

DJANGO_API_URL_KEYWORDS = settings.django_api_endpoint_keywords
INTERNAL_SECRET_KEY = settings.internal_secret_key

async def scrape_and_send_articles():
    # Django에서 키워드 목록 가져오기
    keywords = await fetch_keywords_from_django()
    if not keywords:
        logger.info("키워드를 가져오지 못했습니다.")
        return

    for keyword in keywords:
        title = keyword.get("title")
        keyword_id = keyword.get("id")

        if not title or not keyword_id:
            logger.warning(f"키워드 데이터 누락: {keyword}")
            continue

        # 네이버 뉴스 검색 → 본문 추출 → Django로 전송
        try:
            results = await search_news(title)
            if not results:
                logger.info(f"뉴스 검색 결과 없음: {title}")
                continue

            first = results[0]
            origin_link = first.get("originallink")
            if not origin_link:
                logger.info(f"뉴스 링크 없음: {title}")
                continue

            content = await extract_article_content(origin_link)
            if not content:
                logger.info(f"기사 본문 추출 실패: {title}")
                continue

            payload = {
                "keyword_id": keyword_id,
                "title": title,
                "origin_link": origin_link,
                "content": content,
            }

            await send_articles_to_django(payload)
            logger.info(f"기사 전송 성공: {title}")

        except Exception as e:
            logger.error(f"[ERROR] '{title}' 처리 중 에러: {e}", exc_info=True)