from urllib.parse import urlparse

from app.common.constants.category import CATEGORY_META_MAP
from app.common.logger import get_logger
from app.common.utils.html_utils import clean_article_content, clean_html
from app.features.internal.djnago_client import (
    fetch_keywords_from_django,
    send_articles_to_django,
)
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.scraper.blog_scraper import (
    extract_blog_content,
)
from app.features.internal.fetch_article.scraper.news_scraper import (
    extract_news_content,
)

logger = get_logger(__name__)


def build_origin_link(item: dict) -> str:
    try:
        bloggerlink = item.get("bloggerlink", "")  # ex: blog.naver.com/ggm0724
        # bloggerlink가 'blog.naver.com/ggm0724' 같은 형태면,
        # https:// 붙여서 urlparse로 파싱 후 path에서 아이디만 뽑기
        if not bloggerlink.startswith("http"):
            bloggerlink = "https://" + bloggerlink
        parsed_blogger = urlparse(bloggerlink)
        blog_id = parsed_blogger.path.strip("/")

        link = item.get("link", "")  # ex: https://blog.naver.com/ggm0724/223694021789
        parsed_link = urlparse(link)
        path_parts = parsed_link.path.strip("/").split("/")
        post_id = path_parts[-1] if path_parts else ""

        if not blog_id or not post_id:
            logger.warning(f"[블로그 링크 조합 실패 - 아이디 또는 포스트ID 없음] item={item}")
            return ""

        return f"https://blog.naver.com/{blog_id}/{post_id}"

    except Exception as e:
        logger.warning(f"[블로그 링크 조합 실패] item={item}, error={e}")
        return ""


async def scrape_and_send_articles():

    # 1. Django에서 키워드 목록 받아오기
    keywords = await fetch_keywords_from_django()
    logger.info(f"fetch_keywords_from_django 결과: {keywords}")
    if not keywords:
        logger.info("키워드를 가져오지 못했습니다.")
        return

    all_results = []

    # 2. 키워드별 처리
    for keyword in keywords:
        if not isinstance(keyword, dict):
            continue

        title = keyword.get("title")
        keyword_id = keyword.get("id")
        category = keyword.get("category")

        if not title or not keyword_id or not category:
            logger.warning(f"키워드 데이터 누락 또는 카테고리 없음: {keyword}")
            continue

        # 카테고리별 쿼리, 타입 정보 가져오기
        category_info = CATEGORY_META_MAP.get(category)
        if not category_info:
            logger.warning(f"알 수 없는 카테고리: {category}")
            continue

        query = category_info["query"]
        search_type = category_info["type"]

        logger.info(f"처리 중 키워드: id={keyword_id}, title={title}, category={category}, type={search_type}")

        try:
            # search_news에 query와 타입 넘겨주기
            # ★ search_news 호출 직후 ★
            logger.info(f"search_news 호출: query={query}, type={search_type}")
            results = await search_news(query, type=search_type, display=2)
            logger.debug(f"search_news 결과 개수: {len(results) if results else 'None or empty'}")

            if not results:
                logger.info(f"검색 결과 없음: {query} ({search_type})")
                continue

            scraped_articles = []

            # 4. 뉴스/블로그별 본문 추출 및 정제
            for result in results:
                logger.info(f"전체 result: {result}")
                logger.info(f"origin_link raw: {result.get('link')}")  # 블로그 타입의 경우 link가 원본 주소
                # ★ origin_link (url) 존재 여부 확인 ★
                if search_type == "news":
                    origin_link = result.get("originallink")
                else:
                    origin_link = build_origin_link(result)

                logger.info(f"검색 결과 origin_link: {origin_link}")

                if not origin_link:
                    logger.info(f"origin_link 없음. result: {result}")
                    continue

                # ★ 본문 추출 함수 호출 전 ★
                logger.info(f"본문 추출 시도: {origin_link}")

                if search_type == "news":
                    content = await extract_news_content(origin_link)
                else:
                    content = await extract_blog_content(origin_link)

                # ★ 본문 길이 및 상태 로그 ★
                logger.info(f"본문 길이: {len(content) if content else '없음'}, origin_link: {origin_link}")

                if not content:
                    logger.info(f"본문 추출 실패: {origin_link}")
                    continue

                # ★ 정제 후 본문 길이 등 추가 로그 가능 ★
                cleaned_content = clean_article_content(content)
                logger.debug(f"정제 후 본문 길이: {len(cleaned_content)}")

                # ★ payload 생성 직전, 데이터 점검 로그 ★
                logger.info(f"스크랩된 기사 제목: {clean_html(result.get('title'))} (keyword_id={keyword_id})")

                payload = {
                    "keyword_id": keyword["id"],
                    "title": clean_html(result.get("title")),
                    "origin_link": origin_link,
                    "content": cleaned_content,
                }
                scraped_articles.append(payload)

            # 5. 수집한 기사 일괄 Django로 전송 전 ★
            if scraped_articles:
                logger.info(f"수집된 기사 수: {len(scraped_articles)} - Django 전송 시작")
                result = await send_articles_to_django(scraped_articles)
                logger.info(f"기사 전송 성공: {result}")
                all_results.append(result)  # 결과 누적

        except Exception as e:
            logger.error(f"[ERROR] '{title}' 처리 중 에러: {e}", exc_info=True)

    if all_results:
        return all_results  # 여러 결과 반환
    else:
        return {"message": "수집된 기사가 없습니다."}
