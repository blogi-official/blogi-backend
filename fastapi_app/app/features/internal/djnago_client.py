import json
from typing import List, Dict, Union

from app.common.http_client import post_json, get_json
from app.common.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

async def fetch_keywords_from_django():
    headers = {"X-Internal-Sec  `ret": settings.internal_secret_key}
    return await get_json(settings.django_api_endpoint_keywords_get, headers=headers)

async def send_keywords_to_django(data_list):
    headers = {"X-Internal-Secret": settings.internal_secret_key}
    return await post_json(settings.django_api_endpoint_keywords_post, data_list, headers)

async def send_articles_to_django(data_list: Union[Dict[str, str], List[Dict[str, str]]]):
    headers = {
        "X-Internal-Secret": settings.internal_secret_key,
        "Content-Type": "application/json",
    }
    # 리스트가 아닐 경우, 리스트로 감싸기
    if not isinstance(data_list, list):
        data_list = [data_list]

    logger.info(f"[send_articles_to_django] Django API 요청 시작 - 전송할 데이터 개수: {len(data_list)}")
    logger.debug(f"[send_articles_to_django] 요청 데이터 내용: {json.dumps(data_list, ensure_ascii=False)}")

    try:
        response = await post_json(settings.django_api_endpoint_articles_post, data_list, headers)
        logger.info(f"[send_articles_to_django] Django API 요청 성공")
        logger.debug(f"[send_articles_to_django] Django API 응답 데이터: {json.dumps(response, ensure_ascii=False)}")
        return response
    except Exception as e:
        logger.error(f"[send_articles_to_django] Django API 요청 실패: {e}")
        raise
    #return await post_json(settings.django_api_endpoint_articles_post, data_list, headers)