from app.common.logger import get_logger
from app.common.utils.html_utils import clean_article_content, clean_html
from app.features.internal.djnago_client import (
    fetch_keywords_from_django,
    send_articles_to_django,
)
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.scraper.naver_scraper import (
    extract_article_content,
)

logger = get_logger(__name__)


async def scrape_and_send_articles():
    # 1. Django에서 키워드 목록 받아오기
    keywords = await fetch_keywords_from_django()
    if not keywords:
        logger.info("키워드를 가져오지 못했습니다.")
        return

    # 2. 키워드별 처리
    for keyword in keywords:
        if not isinstance(keyword, dict):
            continue

        title = keyword.get("title")
        keyword_id = keyword.get("id")

        if not title or not keyword_id:
            logger.warning(f"키워드 데이터 누락: {keyword}")
            continue

        logger.debug(f"처리 중 키워드: id={keyword_id}, title={title}")

        try:
            # 3. 네이버 뉴스 display개 검색
            results = await search_news(title, display=3)
            if not results:
                logger.info(f"뉴스 검색 결과 없음: {title}")
                continue

            scraped_articles = []

            # 4. 뉴스별 본문 추출 및 정제
            for result in results:
                origin_link = result.get("originallink")
                if not origin_link:
                    continue

                content = await extract_article_content(origin_link)
                if not content:
                    logger.info(f"본문 추출 실패: {origin_link}")
                    continue

                cleaned_content = clean_article_content(content)

                payload = {
                    "keyword_id": keyword["id"],
                    "title": clean_html(result.get("title")),
                    "origin_link": origin_link,
                    "content": cleaned_content,
                }
                scraped_articles.append(payload)

            # 5. 수집한 기사 일괄 Django로 전송
            if scraped_articles:
                result = await send_articles_to_django(scraped_articles)
                logger.info(f"기사 전송 성공: {title}")

                return result

        except Exception as e:
            logger.error(f"[ERROR] '{title}' 처리 중 에러: {e}", exc_info=True)

    return {"message": "수집된 기사가 없습니다."}
