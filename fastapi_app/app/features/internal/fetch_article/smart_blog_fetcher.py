# app/features/internal/fetch_article/smart_blog_fetcher.py

import logging
from typing import Optional

from app.common.utils.html_utils import clean_article_content, clean_html
from app.common.utils.text import extract_first_word
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.scraper.blog_scraper import (
    extract_blog_content,
)
from app.features.internal.fetch_article.utils import build_origin_link

try:
    from konlpy.tag import Okt

    okt = Okt()
except ImportError:
    okt = None

logger = logging.getLogger(__name__)


async def fetch_smart_article(keyword_id: int, title: str) -> Optional[dict]:
    logger.info(f"[SMART 블로그 수집] 시작 - title: {title}")

    # 1. 기본 검색 시도
    results = await search_news(title, type="blog", display=1)
    if results:
        result = results[0]
        origin_link = build_origin_link(result)
        if not origin_link:
            logger.warning(f"[SKIP] origin_link 없음 - item: {result}")
            return None
        content = await extract_blog_content(origin_link)
        if content:
            return _build_article(keyword_id, result, origin_link, content)

    # 2. 형태소 분석기 없으면 fallback 불가
    if not okt:
        logger.warning("[NLP] 형태소 분석기 미지원 → fallback 중단")
        return None

    # 3. NLP 기반 fallback
    first_word = extract_first_word(title)
    logger.info(f"[FIRST WORD] 추출 결과: {first_word}")

    nouns = okt.nouns(title)
    if not nouns:
        logger.warning("[NLP] 명사 추출 결과 없음 → fallback 중단")
        return None

    filtered_nouns = [n for n in nouns if n not in first_word and not first_word.startswith(n)]
    logger.info(f"[NLP] 명사 필터링 결과: {filtered_nouns}")

    # 4. 2-gram fallback 시도
    for i in range(len(filtered_nouns) - 1):
        phrase = f"{first_word} {filtered_nouns[i]} {filtered_nouns[i+1]}"
        logger.info(f"[TRY] 2-gram fallback 검색: {phrase}")
        article = await try_fallback_search(keyword_id, phrase)
        if article:
            return article

    # 5. 단일 명사 fallback 시도
    for noun in filtered_nouns:
        phrase = f"{first_word} {noun}"
        logger.info(f"[TRY] 단일명사 fallback 검색: {phrase}")
        article = await try_fallback_search(keyword_id, phrase)
        if article:
            return article

    logger.warning(f"[FAIL] 블로그 본문 수집 실패 - title: {title}")
    return None


async def try_fallback_search(keyword_id: int, phrase: str) -> Optional[dict]:
    results = await search_news(phrase, type="blog", display=1)
    if not results:
        return None

    result = results[0]
    origin_link = build_origin_link(result)

    if origin_link is None:
        logger.warning(f"[SKIP] origin_link 없음 - phrase: {phrase}")
        return None

    content = await extract_blog_content(origin_link)
    if content:
        return _build_article(keyword_id, result, origin_link, content)
    return None


def _build_article(keyword_id: int, result: dict, origin_link: str, content: str) -> dict:
    return {
        "keyword_id": keyword_id,
        "title": clean_html(result.get("title", "")),
        "origin_link": origin_link,
        "content": clean_article_content(content),
    }
