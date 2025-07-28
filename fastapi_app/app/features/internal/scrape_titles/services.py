import json
import re
from datetime import datetime
from typing import Dict, List

import httpx
from dateutil.parser import isoparse

from app.common.logger import get_logger
from app.core.config import settings
from app.features.internal.scrape_titles.config import DJANGO_API_ENDPOINT
from app.features.internal.scrape_titles.naver_scraper import scrape_titles

logger = get_logger(__name__)


# 키워드 특수문자 제거 및 날짜 정제
def clean_raw_data(item: dict) -> dict:
    if "title" in item:
        item["title"] = re.sub(r"[^\w\s가-힣\-\.,]", "", item["title"])

    if "collected_at" in item:
        try:
            dt = isoparse(item["collected_at"])
            item["collected_at"] = dt.isoformat()
        except Exception:
            item["collected_at"] = datetime.now().isoformat()

    return item


# ISO 날짜 형식이 아닐 경우 현재 시각으로 대체
def parse_collected_at(raw_date_str: str) -> str:
    try:
        dt = isoparse(raw_date_str)
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"날짜 변환 실패, 기본값 사용: {raw_date_str}, 에러: {e}")
        return datetime.now().isoformat()


# Django 백엔드로 POST 요청 전송
async def call_django_api(data_list: List[Dict[str, str]]):
    headers = {
        "X-Internal-Secret": settings.internal_secret_key or "",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(DJANGO_API_ENDPOINT, json=data_list, headers=headers)
        logger.info(f"Django response status: {response.status_code}")
        logger.info(f"원본 응답 본문: {response.text}")

        try:
            data = response.json()
        except Exception as e:
            logger.error("JSON parsing error:", exc_info=True)
            raise RuntimeError("Django API 응답 오류")

        if response.status_code not in (200, 201):
            logger.error(f"Django API 응답 오류: status={response.status_code}, message={data.get('message')}")
            raise RuntimeError("Django API 응답 오류")

        return data


# 전체 스크래핑
async def fetch_and_send_to_django():
    try:
        logger.info("[DEBUG] scrape_titles() 시작")
        keywords = await scrape_titles()

        # 크롤링 데이터 전체를 먼저 clean_raw_data로 정제
        keywords = [clean_raw_data(k) for k in keywords]

        # collected_at 날짜 다시 한번 포맷 보정
        for item in keywords:
            item["collected_at"] = parse_collected_at(item.get("collected_at", ""))

        logger.info(f"[DEBUG] scrape_titles() 결과: {len(keywords)}개 수집")

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

        logger.info(
            "Django API로 보내는 데이터:\n%s",
            json.dumps(keywords, ensure_ascii=False, indent=2),
        )

        data = await call_django_api(keywords)
        return data

    except Exception as e:
        logger.error("[ERROR] 네이버 페이지 파싱 중 에러 발생:", exc_info=True)
        raise RuntimeError("네이버 페이지 파싱 중 오류가 발생했습니다.") from e
