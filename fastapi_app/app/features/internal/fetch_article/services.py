# app/features/internal/fetch_article/services.py
from app.common.constants.category import CATEGORY_META_MAP
from app.common.logger import get_logger
from app.features.internal.django_client import (
    deactivate_keyword,
    fetch_keywords_from_django,
    send_articles_to_django,
)

# 루프마다 컨텍스트 정리
from app.features.internal.fetch_article.scraper.playwright_browser import (
    close_all_contexts,
)

# 블로그용 (별칭으로)
from app.features.internal.fetch_article.smart_blog_fetcher import (
    fetch_smart_article as fetch_smart_blog,
)

# 뉴스용
from app.features.internal.fetch_article.smart_news_fetcher import fetch_smart_article

logger = get_logger(__name__)


async def scrape_and_send_articles():
    """
    한 런(run) 안에서 같은 키워드/같은 URL로 재시도되는 중복을 차단합니다.
    - attempts_by_keyword: 동일 keyword_id가 같은 run에서 2회 이상 들어오면 비활성화하고 스킵
    - seen_urls: 동일 origin_link(풀 URL) 재등장 시 저장 스킵 + 키워드 비활성화
    외부 시그니처/반환값은 변경하지 않습니다(None).
    """
    attempts_by_keyword: dict[int, int] = {}
    seen_urls: set[str] = set()

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
            try:
                await deactivate_keyword(keyword_id)
            except Exception as e:
                logger.warning(f"[WARN] deactivate 실패(필수 누락): {keyword_id} - {e}")
            continue

        # 🔒 동일 run 중복 가드: 같은 키워드를 같은 run에서 다시 받으면 2회차부터 비활성화
        attempts_by_keyword[keyword_id] = attempts_by_keyword.get(keyword_id, 0) + 1
        if attempts_by_keyword[keyword_id] > 1:
            logger.warning(
                f"[SKIP-LOCAL] 동일 run 내 중복 배정: {keyword_id} (attempt={attempts_by_keyword[keyword_id]})"
            )
            try:
                await deactivate_keyword(keyword_id)
            except Exception as e:
                logger.warning(f"[WARN] deactivate 실패(중복 배정): {keyword_id} - {e}")
            continue

        category_info = CATEGORY_META_MAP.get(category)
        if not category_info:
            logger.warning(f"[SKIP] 알 수 없는 카테고리: {category}")
            try:
                await deactivate_keyword(keyword_id)
            except Exception as e:
                logger.warning(f"[WARN] deactivate 실패(카테고리): {keyword_id} - {e}")
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
                try:
                    await deactivate_keyword(keyword_id)
                except Exception as e:
                    logger.warning(f"[WARN] deactivate 실패(None 결과): {keyword_id} - {e}")
                continue

            if not isinstance(article, dict):
                logger.warning(f"[FAIL] 결과 형식 오류: keyword_id={keyword_id}, article={article}")
                try:
                    await deactivate_keyword(keyword_id)
                except Exception as e:
                    logger.warning(f"[WARN] deactivate 실패(형식 오류): {keyword_id} - {e}")
                continue

            # 🧱 동일 run 내 동일 URL(원문) 중복 저장 가드
            origin = (article.get("origin_link") or article.get("origin") or "").strip()
            if origin:
                if origin in seen_urls:
                    logger.warning(f"[SKIP-LOCAL] 동일 run 내 중복 URL: {origin} (keyword_id={keyword_id})")
                    try:
                        await deactivate_keyword(keyword_id)
                    except Exception as e:
                        logger.warning(f"[WARN] deactivate 실패(중복 URL): {keyword_id} - {e}")
                    continue
                seen_urls.add(origin)

            logger.info(f"[SUCCESS] 수집 완료: keyword_id={keyword_id}, title={article.get('title')}")
            result = await send_articles_to_django([article])
            logger.info(f"[SEND] Django 저장 결과: {result}")

        except Exception as e:
            logger.error(
                f"[ERROR] 처리 중 예외 발생: keyword_id={keyword_id}, title={title} - {e}",
                exc_info=True,
            )
            try:
                await deactivate_keyword(keyword_id)
            except Exception as de:
                logger.warning(f"[WARN] deactivate 실패(예외 처리): {keyword_id} - {de}")
            continue

        finally:
            # ✅ 매 키워드 처리 후 남은 컨텍스트 전부 닫기 (누수 차단)
            await close_all_contexts()
            # (옵션) 누적 메모리가 가끔 안내려가면 주기적으로 브라우저 완전 리사이클:
            # if attempts_by_keyword.get(keyword_id, 0) % 10 == 0:
            #     await recycle_browser()
