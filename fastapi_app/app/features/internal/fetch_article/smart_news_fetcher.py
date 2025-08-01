import logging
from typing import Optional

from app.common.utils.html_utils import clean_article_content, clean_html
from app.common.utils.text import extract_first_word
from app.features.internal.fetch_article.naver_api import search_news
from app.features.internal.fetch_article.scraper.news_scraper import (
    extract_news_content,
)

try:
    from konlpy.tag import Okt

    okt = Okt()
except ImportError:
    okt = None

logger = logging.getLogger(__name__)


async def fetch_smart_article(keyword_id: int, title: str) -> Optional[dict]:
    logger.info(f"[SMART 뉴스 수집] 시작 - title: {title}")

    # 1. 기본 검색 시도
    result = await try_search_and_extract(title)
    if result:
        return build_article(keyword_id, result)

    # 2. 형태소 분석기 필요
    if not okt:
        logger.warning("[NLP] 형태소 분석기 미지원 → fallback 중단")
        return None

    # 3. 형태소 분석
    first_word = extract_first_word(title)
    nouns = okt.nouns(title)

    if not nouns:
        logger.warning("[NLP] 명사 추출 결과 없음 → fallback 중단")
        return None

    logger.info(f"[NLP] 명사 추출 결과: {nouns}")
    filtered = [n for n in nouns if n not in first_word and not first_word.startswith(n)]
    logger.info(f"[NLP] 중복 제거 후 명사: {filtered}")

    # 4. 2-gram fallback
    for i in range(len(filtered) - 1):
        phrase = f"{first_word} {filtered[i]} {filtered[i+1]}"
        logger.info(f"[TRY] 2-gram fallback 검색: {phrase}")
        result = await try_search_and_extract(phrase)
        if result:
            return build_article(keyword_id, result)

    # 5. 단일 명사 fallback
    for noun in filtered:
        phrase = f"{first_word} {noun}"
        logger.info(f"[TRY] 단일명사 fallback 검색: {phrase}")
        result = await try_search_and_extract(phrase)
        if result:
            return build_article(keyword_id, result)

    logger.warning(f"[FAIL] 뉴스 본문 수집 실패 - title: {title}")
    return None


async def try_search_and_extract(phrase: str) -> Optional[dict]:
    results = await search_news(phrase, type="news", display=1)
    if not results:
        return None

    link = results[0]["link"]
    content = await extract_news_content(link)
    if not content:
        return None

    return {
        "title": results[0]["title"],
        "origin_link": link,
        "content": content,
    }


def build_article(keyword_id: int, data: dict) -> dict:
    return {
        "keyword_id": keyword_id,
        "title": clean_html(data["title"]),
        "origin_link": data["origin_link"],
        "content": clean_article_content(data["content"]),
    }
