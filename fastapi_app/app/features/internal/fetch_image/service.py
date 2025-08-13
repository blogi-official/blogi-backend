import logging

from fastapi import HTTPException

from app.common.http_client import get_raw_json, patch_json, post_json
from app.common.utils.url_utils import join_url
from app.core.config import settings

from .smart_image_fetcher import fetch_images_smart_with_threshold

logger = logging.getLogger(__name__)


async def fetch_and_save_images() -> list[str]:
    results: list[str] = []

    while True:
        try:
            # 1. 수집 대상 keyword 조회
            keyword_data = await get_raw_json(
                join_url(
                    settings.django_api_url,
                    settings.django_api_endpoint_keyword_image_target,
                )
            )

            # 대상 없으면 종료
            if not keyword_data or "id" not in keyword_data or "title" not in keyword_data:
                logger.info("더 이상 수집할 이미지 대상이 없습니다. 종료합니다.")
                break

            keyword_id = keyword_data["id"]
            title = keyword_data["title"]
            logger.info(f"[FETCH] keyword_id={keyword_id}, title='{title}'")

            # 2. Kakao 이미지 수집 (최대 3개 확보까지 스마트 시도)
            image_urls = await fetch_images_smart_with_threshold(title)
            image_urls = image_urls[:3]
            logger.info(f"[FETCH] keyword_id={keyword_id}, image_urls={image_urls}")

            # 3. 이미지 없음 처리
            if not image_urls:
                logger.warning(f"[SKIP] keyword_id={keyword_id} - 이미지 없음, 수집 완료 처리")
                await patch_json(
                    join_url(
                        settings.django_api_url,
                        settings.django_api_endpoint_mark_collected.replace("{id}", str(keyword_id)),
                    ),
                    data={},
                )
                continue

            # 4. Django 이미지 저장 요청
            await post_json(
                join_url(settings.django_api_url, settings.django_api_endpoint_save_images),
                data={"keyword_id": keyword_id, "images": image_urls},
            )
            logger.info(f"[POST] keyword_id={keyword_id} - 이미지 저장 성공")

            # 5. 수집 완료 표시
            await patch_json(
                join_url(
                    settings.django_api_url,
                    settings.django_api_endpoint_mark_collected.replace("{id}", str(keyword_id)),
                ),
                data={},
            )
            logger.info(f"[PATCH] keyword_id={keyword_id} - 수집 완료 표시 성공")

            results.extend(image_urls)

        except RuntimeError as e:
            if "status=404" in str(e):
                logger.info("[SKIP] 수집 대상 키워드 없음 (404)")
                break
            logger.error(f"[ERROR] RuntimeError: {e}", exc_info=True)
            continue

        except Exception as e:
            logger.error(f"[FATAL] 이미지 수집 중 예외 발생: {e}", exc_info=True)
            continue

    return results
