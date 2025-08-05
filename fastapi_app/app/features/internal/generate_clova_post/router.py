# fastapi_app/app/features/internal/generate_clova_post/router.py

import traceback

from fastapi import APIRouter, HTTPException, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from app.core.config import settings

from .schema import GenerateClovaPostRequest, GenerateClovaPostResponse
from .service import fetch_generated_post_preview, process_clova_generation

router = APIRouter()
api_key_header = APIKeyHeader(name="x-internal-secret", auto_error=True)


@router.post(
    "/generate-clova-post",
    response_model=GenerateClovaPostResponse,
    tags=["[Internal] Clova 콘텐츠 생성"],
    summary="Clova 콘텐츠 생성 및 저장 (005~009 통합)",
)
async def generate_clova_post_handler(
    payload: GenerateClovaPostRequest, x_internal_secret: str = Security(api_key_header)
):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    try:
        result = await process_clova_generation(payload)
        return result

    except Exception:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Clova 콘텐츠 생성 중 오류가 발생했습니다."},
        )


@router.post(
    "/generated-posts/preview",
    response_model=GenerateClovaPostResponse,
    tags=["[Internal] Clova 콘텐츠 생성"],
    summary="Clova 콘텐츠 미리보기 (저장 없이 생성만)",
)
async def generate_clova_preview_handler(
    payload: GenerateClovaPostRequest, x_internal_secret: str = Security(api_key_header)
):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    try:

        preview = await fetch_generated_post_preview(
            keyword_id=payload.keyword_id,
            user_id=payload.user_id,
        )

        if preview:
            return GenerateClovaPostResponse(
                post_id=preview["post_id"],
                created_at=preview["created_at"],
                status="cached",
                error_message=None,
                from_cache=True,  # optional if included in schema
            )
        else:
            return GenerateClovaPostResponse(
                post_id=None,
                created_at=None,
                status="not_found",
                error_message=None,
                from_cache=False,
            )

    except Exception:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Clova 미리보기 생성 중 오류가 발생했습니다."},
        )
