from app.common.logger import get_logger
from app.features.internal.django_client import (
    deactivate_keyword,
    fetch_article_with_images,
    fetch_generated_post_preview,
    log_clova_failure_to_django,
    log_clova_success_to_django,
    send_generated_post_to_django,
)
from app.features.internal.generate.clova_client import generate_clova_post
from app.features.internal.generate_clova_post.schema import (
    GenerateClovaPostRequest,
    GenerateClovaPostResponse,
)

logger = get_logger(__name__)


async def process_clova_generation(payload: GenerateClovaPostRequest) -> GenerateClovaPostResponse:
    """
    Clova 콘텐츠 생성 전체 프로세스
    1. 이미 생성된 글이 있으면 리턴
    2. 기사 조회
    3. Clova 요청 → 실패 시 비활성화 + 로그
    4. 성공 시 Django에 저장 + 성공 로그
    """
    try:
        # 0. 생성된 글 미리보기 확인
        preview = await fetch_generated_post_preview(
            keyword_id=payload.keyword_id,
            user_id=payload.user_id,
        )
        if preview:
            logger.info(f"[SKIP] 이미 생성된 글 존재 - post_id={preview['post_id']}")
            return GenerateClovaPostResponse(
                status="success",
                post_id=preview["post_id"],
                created_at=preview["created_at"],
                error_message=None,
                from_cache=True,
            )

        # 1. 기사 조회
        article_data = await fetch_article_with_images(payload.keyword_id)
        if not article_data or not article_data.get("content"):
            raise ValueError("기사 내용이 비어 있습니다.")

        logger.info(f"[STEP 1] 기사 조회 완료 - keyword_id={payload.keyword_id}")

        # 2. Clova 생성 요청 (이미지 포함된 HTML까지 생성)
        image_urls = article_data.get("image_urls", [])
        clova_result = await generate_clova_post(
            title=article_data["title"],
            article_content=article_data["content"],
            image_urls=image_urls,
        )

        if clova_result.get("status") != "success":
            error_message = clova_result.get("error_message", "Clova 생성 실패")
            logger.warning(f"[STEP 2] Clova 생성 실패 - {error_message}")

            await log_clova_failure_to_django(
                {
                    "keyword_id": payload.keyword_id,
                    "user_id": payload.user_id,
                    "status": "fail",
                    "error_message": error_message,
                }
            )
            await deactivate_keyword(payload.keyword_id)

            return GenerateClovaPostResponse(
                status="fail",
                post_id=None,
                created_at=None,
                error_message=error_message,
                from_cache=False,
            )

        logger.info(f"[STEP 2] Clova 생성 성공 - title={clova_result['title']}")

        # 3. 최종 저장 (Clova에서 이미지 삽입 완료된 content 사용)
        final_content = clova_result["content"]

        save_result = await send_generated_post_to_django(
            {
                "keyword_id": payload.keyword_id,
                "user_id": payload.user_id,
                "title": clova_result["title"],
                "content": final_content,
                "image_1_url": image_urls[0] if len(image_urls) > 0 else None,
                "image_2_url": image_urls[1] if len(image_urls) > 1 else None,
                "image_3_url": image_urls[2] if len(image_urls) > 2 else None,
            }
        )

        await log_clova_success_to_django(
            {
                "keyword_id": payload.keyword_id,
                "user_id": payload.user_id,
                "status": "success",
                "response_time_ms": clova_result.get("response_time_ms", 0),
            }
        )

        logger.info(f"[STEP 3] Django 저장 완료 - post_id={save_result['post_id']}")

        return GenerateClovaPostResponse(
            status="success",
            post_id=save_result["post_id"],
            created_at=save_result["created_at"],
            error_message=None,
            from_cache=False,
        )

    except Exception as e:
        logger.error(f"[FATAL] Clova 생성 중 예외 발생: {e}", exc_info=True)
        raise
