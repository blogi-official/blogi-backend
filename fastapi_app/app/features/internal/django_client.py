import json
from typing import Dict, List, Union

from app.common.http_client import get_json, get_raw_json, patch_json, post_json
from app.common.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


# GET
async def fetch_keywords_from_django():
    return await get_raw_json(settings.django_api_endpoint_keywords_get)


# POST
async def send_keywords_to_django(data_list):
    return await post_json(settings.django_api_endpoint_keywords_post, data_list)


# POST
async def send_articles_to_django(
    data_list: Union[Dict[str, str], List[Dict[str, str]]],
):
    # 리스트가 아닐 경우, 리스트로 감싸기
    if not isinstance(data_list, list):
        data_list = [data_list]

    logger.info(f"[send_articles_to_django] Django API 요청 시작 - 전송할 데이터 개수: {len(data_list)}")
    logger.debug(f"[send_articles_to_django] 요청 데이터 내용: {json.dumps(data_list, ensure_ascii=False)}")

    try:
        response = await post_json(settings.django_api_endpoint_articles_post, data_list)
        logger.info(f"[send_articles_to_django] Django API 요청 성공")
        logger.debug(f"[send_articles_to_django] Django API 응답 데이터: {json.dumps(response, ensure_ascii=False)}")
        return response
    except Exception as e:
        logger.error(f"[send_articles_to_django] Django API 요청 실패: {e}")
        raise


# PATCH
async def deactivate_keyword(keyword_id: int):
    try:
        await patch_json(
            f"{settings.django_api_url}/api/internal/keywords/{keyword_id}/deactivate/",
            data={},
        )
        logger.info(f"[PATCH] keyword_id={keyword_id} - is_active=False 처리 완료")
    except Exception as e:
        logger.error(f"[PATCH FAIL] keyword_id={keyword_id} - 비활성화 실패: {e}")
