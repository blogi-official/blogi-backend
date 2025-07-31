import logging

from app.common.http_client import get_raw_json, patch_json, post_json
from app.core.config import settings

from .kakao_client import fetch_kakao_images
from .smart_image_fetcher import fetch_images_smart_with_threshold

logger = logging.getLogger(__name__)


async def fetch_and_save_images() -> list[str]:
    try:
        # 1. 수집 대상 keyword 조회
        keyword_data = await get_raw_json(
            f"{settings.django_api_url}{settings.django_api_endpoint_keyword_image_target}"
        )

        # 응답이 None 또는 잘못된 형식일 경우 방어 처리
        if not keyword_data or "id" not in keyword_data or "title" not in keyword_data:
            logger.warning("[SKIP] keyword_data 응답이 유효하지 않습니다: %s", keyword_data)
            return []

        keyword_id = keyword_data["id"]
        title = keyword_data["title"]
        logger.info(f"[FETCH] keyword_id={keyword_id}, title='{title}'")

        # 2. Kakao 이미지 수집 (최대 3개 확보까지 스마트 시도)
        image_urls = await fetch_images_smart_with_threshold(title)
        image_urls = image_urls[:3]  #  최대 3개 제한
        logger.info(f"[FETCH] keyword_id={keyword_id}, image_urls={image_urls}")

        # 3. 저장 조건 확인
        if not image_urls:
            logger.warning(f"[SKIP] keyword_id={keyword_id}, '{title}' 키워드에 대한 이미지 없음")
            return []

        # 4. Django 이미지 저장 요청
        try:
            logger.info(f"[POST] keyword_id={keyword_id} - Django 이미지 저장 요청")
            await post_json(
                f"{settings.django_api_url}{settings.django_api_endpoint_save_images}",
                data={"keyword_id": keyword_id, "images": image_urls},
            )
            logger.info(f"[POST] keyword_id={keyword_id} - 이미지 저장 성공")
        except Exception as e:
            logger.error(f"[ERROR] keyword_id={keyword_id} - 이미지 저장 실패: {e}")
            raise

        # 5. 수집 완료 처리
        try:
            logger.info(f"[PATCH] keyword_id={keyword_id} - 수집 완료 처리 중")
            await patch_json(  # PATCH 방식으로 변경
                f"{settings.django_api_url}{settings.django_api_endpoint_mark_collected}".replace(
                    "{id}", str(keyword_id)
                ),
                data={},
            )
            logger.info(f"[PATCH] keyword_id={keyword_id} - 수집 완료 표시 성공")
        except Exception as e:
            logger.error(f"[ERROR] keyword_id={keyword_id} - 수집 완료 표시 실패: {e}")
            raise

        logger.info(f"[DONE] keyword_id={keyword_id} - 전체 이미지 수집 프로세스 완료")
        return image_urls

    except Exception as e:
        logger.error(f"[FATAL] 이미지 수집 프로세스 실패: {e}", exc_info=True)
        raise
