# http_client.py

import logging
from typing import Any, Dict
import httpx

logger = logging.getLogger(__name__)

async def get_json(url: str, headers: Dict[str, str] = None) -> Any:
    logger.info(f"API 호출 URL: {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
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


async def post_json(url: str, data: Any, headers: Dict[str, str] = None) -> Any:
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=default_headers)
        logger.info(f"POST {url} response status: {response.status_code}")
        logger.debug(f"Response text (shortened): {response.text[:50]}...")

        if response.status_code not in (200, 201):
            logger.error(f"API 응답 오류: status={response.status_code}, text={response.text!r}")
            raise RuntimeError("API 응답 오류")

        try:
            res_data = response.json()
        except Exception:
            logger.error("JSON parsing error", exc_info=True)
            logger.error(f"응답 내용이 JSON이 아닙니다: {response.text!r}")
            raise RuntimeError("API 응답 오류")

        return res_data
