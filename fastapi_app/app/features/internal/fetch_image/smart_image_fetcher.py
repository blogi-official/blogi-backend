import logging
from typing import List

from app.common.logger import get_logger
from app.common.utils.text import extract_first_word
from app.features.internal.fetch_image.kakao_client import fetch_kakao_images

try:
    from konlpy.tag import Okt

    okt = Okt()
except ImportError:
    okt = None

logger = get_logger(__name__)


async def fetch_images_smart_with_threshold(title: str, count: int = 3) -> List[str]:
    logger.info(f"[TITLE] {title}")

    # 1. 원본 키워드로 시도
    image_urls = await fetch_kakao_images(title, count)
    logger.info(f"[TRY] 원문 그대로: {title} → {len(image_urls)}개")
    if len(image_urls) >= count:
        logger.info(f"[SELECTED] ✅ 원문으로 {count}개 확보 성공")
        return image_urls

    # 2. 형태소 분석 불가 시 중단
    if not okt:
        logger.warning("[NLP] 형태소 분석기 미지원 → fallback 불가")
        return image_urls

    # 3. 첫 단어 추출
    first_word = extract_first_word(title)
    logger.info(f"[FIRST WORD] 추출 결과: {first_word}")

    # 4. 명사 분석
    nouns = okt.nouns(title)
    if not nouns:
        logger.warning("[NLP] 명사 추출 결과 없음 → fallback 중단")
        return image_urls
    logger.info(f"[NLP] 명사 추출 결과: {nouns}")

    # 5. 중복 제거
    filtered_nouns = [noun for noun in nouns if noun not in first_word and not first_word.startswith(noun)]
    logger.info(f"[NLP] 중복 제거 후 명사: {filtered_nouns}")

    # 6. 첫 단어 + 2-gram 조합 시도
    for i in range(len(filtered_nouns) - 1):
        phrase = f"{first_word} {filtered_nouns[i]} {filtered_nouns[i+1]}"
        fallback = await fetch_kakao_images(phrase, count)
        logger.info(f"[TRY] 첫단어 + 2-gram: '{phrase}' → {len(fallback)}개")
        if len(fallback) >= count:
            logger.info(f"[SELECTED] ✅ '{phrase}' 로 {count}개 확보 성공")
            return fallback
        if len(fallback) > len(image_urls):
            image_urls = fallback

    # 7. 첫 단어 + 단일 명사 조합 시도
    for noun in filtered_nouns:
        phrase = f"{first_word} {noun}"
        fallback = await fetch_kakao_images(phrase, count)
        logger.info(f"[TRY] 첫단어 + 명사: '{phrase}' → {len(fallback)}개")
        if len(fallback) >= count:
            logger.info(f"[SELECTED] ✅ '{phrase}' 로 {count}개 확보 성공")
            return fallback
        if len(fallback) > len(image_urls):
            image_urls = fallback

    logger.info(f"[SELECTED] 최종 이미지 {len(image_urls)}개 확보 완료")
    return image_urls
