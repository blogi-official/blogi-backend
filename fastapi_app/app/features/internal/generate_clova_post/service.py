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


def insert_images_into_content(content: str, image_urls: list[str]) -> str:
    """
    HTML 문단(<p>) 또는 \n\n 기준으로 나눈 후 이미지 삽입 (최대 3개)
    """
    if not image_urls:
        return content

    # <p> 태그 기준 분할, 없으면 \n\n 기준
    if "<p>" in content:
        paragraphs = content.split("</p>")
        paragraphs = [p + "</p>" for p in paragraphs if p.strip()]
    else:
        paragraphs = content.split("\n\n")

    num_paragraphs = len(paragraphs)
    num_images = min(len(image_urls), 3)
    insert_positions = [(i + 1) * num_paragraphs // (num_images + 1) for i in range(num_images)]

    for idx, pos in enumerate(insert_positions):
        img_tag = f'<img src="{image_urls[idx]}" alt="대표 이미지 {idx + 1}" style="max-width:100%; margin: 1rem 0;" />'
        paragraphs.insert(pos, img_tag)

    return "\n\n".join(paragraphs)


async def process_clova_generation(payload: GenerateClovaPostRequest) -> GenerateClovaPostResponse:
    """
    Clova 콘텐츠 생성 전체 프로세스
    1. 이미 생성된 글이 있으면 리턴
    2. 기사 조회
    3. Clova 요청 → 실패 시 비활성화 + 로그
    4. 성공 시 이미지 삽입 후 저장 + 성공 로그
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

        # 2. Clova 생성 요청
        clova_result = await generate_clova_post(
            title=article_data["title"],
            content=article_data["content"],
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

        # 3. 이미지 삽입 후 content 완성
        image_urls = article_data.get("image_urls", [])
        final_content = insert_images_into_content(clova_result["content"], image_urls)

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
