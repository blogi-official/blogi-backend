# fastapi_app/app/features/internal/fetch_image/kakao_client.py
import logging
from typing import List, Union

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# 추가: 쿼터 초과를 상위에서 구분 처리하기 위한 전용 예외
class KakaoThrottled(RuntimeError):
    pass


async def fetch_kakao_images(query: str, count: int = 3) -> List[str]:
    """
    Kakao 이미지 검색 API를 사용하여 이미지 URL 리스트를 반환합니다.
    """
    endpoint = "https://dapi.kakao.com/v2/search/image"
    headers = {
        "Authorization": f"KakaoAK {settings.kakao_rest_api_key}",
    }

    # 타입 명시로 mypy 오류 방지
    params: dict[str, Union[str, int]] = {
        "query": query,
        "sort": "accuracy",  # 또는 "recency"
        "page": 1,
        "size": count,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(endpoint, headers=headers, params=params)
        status = response.status_code

        # 쿼터 초과(429) 또는 본문의 RequestThrottled 식별 → 전용 예외로 올림
        if status != 200:
            body_text = response.text
            try:
                body_json = response.json()
            except Exception:
                body_json = {}

            if status == 429 or body_json.get("errorType") == "RequestThrottled":
                logger.warning(f"[KakaoAPI] THROTTLED query='{query}' status={status} body={body_json or body_text}")
                raise KakaoThrottled("Kakao API limit exceeded")

            logger.error(f"[KakaoAPI] 오류 발생: {body_text}")
            raise RuntimeError("Kakao 이미지 API 호출 중 오류가 발생했습니다.")

        logger.info(f"[KakaoAPI] query='{query}' status_code={status}")

        data = response.json()
        images = [item["image_url"] for item in data.get("documents", [])[:count]]
        return images
