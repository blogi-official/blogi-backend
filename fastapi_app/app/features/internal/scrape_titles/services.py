from app.common.logger import get_logger
from app.common.utils.text_utils import clean_raw_data
from app.common.utils.time_utils import parse_collected_at
from app.features.internal.django_client import send_keywords_to_django
from app.features.internal.scrape_titles.naver_scraper import scrape_titles

logger = get_logger(__name__)


# 전체 스크래핑
async def fetch_and_send_to_django():
    try:
        logger.info("scrape_titles() 시작")
        keywords = await scrape_titles()

        # 크롤링 데이터 전체를 먼저 clean_raw_data로 정제
        keywords = [clean_raw_data(k) for k in keywords]

        # collected_at 날짜 다시 한번 포맷 보정
        for item in keywords:
            item["collected_at"] = parse_collected_at(item.get("collected_at", ""))

        logger.info(f"스크래핑 결과: {len(keywords)}개 수집")

        # 공백 제거 후 빈 문자열이 아닌 경우에만 필터링하여 남김
        keywords = [
            k
            for k in keywords
            if all(isinstance(k.get(f), str) and k.get(f).strip() for f in ["title", "category", "source_category"])
        ]

        if not keywords:
            return {
                "message": "수집된 키워드가 없습니다.",
                "created_count": 0,
                "skipped_count": 0,
            }

        # logger.debug("Django API로 보내는 데이터:\n%s", json.dumps(keywords, ensure_ascii=False, indent=2))

        data = await send_keywords_to_django(keywords)
        return data

    except Exception as e:
        logger.error("[ERROR] 네이버 페이지 파싱 중 에러 발생:", exc_info=True)
        raise RuntimeError("네이버 페이지 파싱 중 오류가 발생했습니다.") from e
