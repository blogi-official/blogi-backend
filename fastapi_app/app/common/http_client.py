import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_json(url: str, headers: Optional[Dict[str, str]] = None) -> Any:
    default_headers = {
        "X-Internal-Secret": settings.internal_secret_key or "",
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=default_headers)
        logger.info(f"GET {url} response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")

        try:
            data = response.json()
        except Exception:
            logger.error("JSON parsing error", exc_info=True)
            raise RuntimeError("API 응답 오류")

        if response.status_code != 200:
            logger.error(f"API 응답 오류: status={response.status_code}, message={data.get('message', '')}")
            raise RuntimeError("API 응답 오류")

        return data.get("data", [])


async def post_json(url: str, data: Any, headers: Optional[Dict[str, str]] = None) -> Any:
    default_headers = {
        "X-Internal-Secret": settings.internal_secret_key or "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=default_headers)
        logger.info(f"POST {url} response status: {response.status_code}")
        logger.debug(f"Response text (shortened): {response.text[:50]}...")

        if response.status_code == 204:
            # 204인 경우: 데이터 없음으로 None 반환 (정상 흐름)
            return None

        if response.status_code not in (200, 201):
            logger.error(f"API 응답 오류: status={response.status_code}, text={response.text!r}")
            raise RuntimeError("API 응답 오류")

        try:
            return response.json()
        except Exception:
            logger.error("JSON parsing error", exc_info=True)
            logger.error(f"응답 내용이 JSON이 아닙니다: {response.text!r}")
            raise RuntimeError("API 응답 오류")


# kakao 이미지용


async def get_raw_json(url: str, headers: Optional[Dict[str, str]] = None) -> Any:
    default_headers = {
        "X-Internal-Secret": settings.internal_secret_key or "",
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=default_headers)

    # 디버그 로그
    logger.warning(f"[DEBUG] 요청 URL: {url}")
    logger.warning(f"[DEBUG] 응답 상태코드: {response.status_code}")
    logger.warning(f"[DEBUG] 응답 본문: {response.text[:300]}")

    # 상태코드 먼저 확인 → 200 아니면 무조건 에러 처리
    if response.status_code != 200:
        logger.error(f"[RAW GET] API 응답 오류: status={response.status_code}, body={response.text}")
        raise RuntimeError(f"API 응답 오류: status={response.status_code}")

    # JSON 파싱
    try:
        return response.json()
    except Exception:
        logger.error("RAW JSON parsing error", exc_info=True)
        raise RuntimeError("JSON 파싱 오류")


async def patch_json(url: str, data: dict, headers: Optional[Dict[str, str]] = None) -> Any:
    default_headers = {
        "Content-Type": "application/json",
        "X-Internal-Secret": settings.internal_secret_key or "",
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, json=data, headers=default_headers)
        logger.info(f"[PATCH] {url} response status: {response.status_code}")
        logger.debug(f"[PATCH] Response text: {response.text[:100]}")

        try:
            resp_data = response.json()
        except Exception:
            logger.error("[PATCH] JSON parsing error", exc_info=True)
            raise RuntimeError("API 응답 오류")

        if response.status_code not in (200, 204):
            logger.error(f"[PATCH] API 응답 오류: status={response.status_code}, body={resp_data}")
            raise RuntimeError("API 응답 오류")

        return resp_data
