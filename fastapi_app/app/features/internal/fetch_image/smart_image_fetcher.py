# fastapi_app/app/features/internal/fetch_image/smart_image_fetcher.py
import logging
from typing import List

from app.common.logger import get_logger
from app.common.utils.text import extract_first_word

# ✅ KakaoThrottled 함께 import
from app.features.internal.fetch_image.kakao_client import (
    KakaoThrottled,
    fetch_kakao_images,
)

try:
    from konlpy.tag import Okt

    okt = Okt()
except ImportError:
    okt = None

logger = get_logger(__name__)


async def fetch_images_smart_with_threshold(title: str, count: int = 3) -> List[str]:
    logger.info(f"[TITLE] {title}")

    # ✅ 추가: 키워드당 Kakao 호출 상한(과도한 시도 방지)
    MAX_ATTEMPTS = 4
    attempts = 0

    async def try_fetch(q: str) -> List[str]:
        nonlocal attempts
        if attempts >= MAX_ATTEMPTS:
            return []
        attempts += 1
        return await fetch_kakao_images(q, count)

    # 1) 원문
    image_urls = await try_fetch(title)
    logger.info(f"[TRY] 원문 그대로: {title} → {len(image_urls)}개 (attempts={attempts})")
    if len(image_urls) >= count:
        logger.info(f"[SELECTED] 원문으로 {count}개 확보 성공")
        return image_urls

    # 2) 형태소 분석 불가 시 중단
    if not okt:
        logger.warning("[NLP] 형태소 분석기 미지원 → fallback 불가")
        return image_urls

    # 3) 첫 단어 추출
    first_word = extract_first_word(title)
    logger.info(f"[FIRST WORD] 추출 결과: {first_word}")

    # 4) 명사 분석
    nouns = okt.nouns(title)
    if not nouns:
        logger.warning("[NLP] 명사 추출 결과 없음 → fallback 중단")
        return image_urls
    logger.info(f"[NLP] 명사 추출 결과: {nouns}")

    # 5) 중복 제거
    filtered_nouns = [noun for noun in nouns if noun not in first_word and not first_word.startswith(noun)]
    logger.info(f"[NLP] 중복 제거 후 명사: {filtered_nouns}")

    # 6) 첫 단어 + 2-gram 조합 시도
    for i in range(len(filtered_nouns) - 1):
        if attempts >= MAX_ATTEMPTS:
            break
        phrase = f"{first_word} {filtered_nouns[i]} {filtered_nouns[i+1]}"
        fallback = await try_fetch(phrase)
        logger.info(f"[TRY] 첫단어 + 2-gram: '{phrase}' → {len(fallback)}개 (attempts={attempts})")
        if len(fallback) >= count:
            logger.info(f"[SELECTED] '{phrase}' 로 {count}개 확보 성공")
            return fallback
        if len(fallback) > len(image_urls):
            image_urls = fallback

    # 7) 첫 단어 + 단일 명사 조합 시도
    for noun in filtered_nouns:
        if attempts >= MAX_ATTEMPTS:
            break
        phrase = f"{first_word} {noun}"
        fallback = await try_fetch(phrase)
        logger.info(f"[TRY] 첫단어 + 명사: '{phrase}' → {len(fallback)}개 (attempts={attempts})")
        if len(fallback) >= count:
            logger.info(f"[SELECTED] '{phrase}' 로 {count}개 확보 성공")
            return fallback
        if len(fallback) > len(image_urls):
            image_urls = fallback

    logger.info(f"[SELECTED] 최종 이미지 {len(image_urls)}개 확보 완료 (attempts={attempts})")
    return image_urls
