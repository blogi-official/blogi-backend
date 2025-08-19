import json
from typing import Dict, List, Union
from urllib.parse import urljoin

from app.common.http_client import get_json, get_raw_json, patch_json, post_json
from app.common.logger import get_logger
from app.common.utils.url_utils import join_url
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


# 기사 + 이미지 통합 조회
async def fetch_article_with_images(keyword_id: int):
    url = join_url(
        settings.django_api_url,
        settings.django_api_endpoint_article_detail,
        str(keyword_id),
    )
    return await get_raw_json(url)


# Clova 생성 결과 상세 조회
async def fetch_post_details_from_django(post_id: int):
    endpoint_path = join_url(
        settings.django_api_url, settings.django_api_endpoint_generated_get_patch.format(post_id=post_id)
    )
    url = urljoin(settings.django_api_url, endpoint_path)
    return await get_raw_json(url)


# Clova 생성 결과 저장
async def send_generated_post_to_django(post_data: dict):
    url = join_url(settings.django_api_url, settings.django_api_endpoint_generated_post)
    return await post_json(url, post_data)


# Clova 재생성 결과 수정 (PATCH)
async def update_generated_post_in_django(post_id: int, update_data: dict):
    endpoint_path = join_url(
        settings.django_api_url, settings.django_api_endpoint_generated_get_patch.format(post_id=post_id)
    )
    url = urljoin(settings.django_api_url, endpoint_path)
    return await patch_json(url, update_data)


# Clova 성공 로그 저장
async def log_clova_success_to_django(log_data: dict):
    url = join_url(settings.django_api_url, settings.django_api_endpoint_clova_log_success)
    return await post_json(url, log_data)


# Clova 실패 로그 저장
async def log_clova_failure_to_django(log_data: dict):
    url = join_url(settings.django_api_url, settings.django_api_endpoint_clova_log_fail)
    return await post_json(url, log_data)


# 키워드 비활성화 처리 (PATCH)
async def deactivate_keyword(keyword_id: int):
    try:
        url = join_url(
            settings.django_api_url,
            settings.django_api_endpoint_keyword_deactivate.format(id=keyword_id),
        )
        await patch_json(url, data={})
        logger.info(f"[PATCH] keyword_id={keyword_id} - is_active=False 처리 완료")
    except Exception as e:
        logger.error(f"[PATCH FAIL] keyword_id={keyword_id} - 비활성화 실패: {e}")


# 생성된 글 미리보기 요청 (존재 시 응답)
async def fetch_generated_post_preview(keyword_id: int, user_id: int):
    url = join_url(
        settings.django_api_url,
        settings.django_api_endpoint_generated_post_preview,
    )
    payload = {"keyword_id": keyword_id, "user_id": user_id}
    return await post_json(url, payload)
