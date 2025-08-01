# fastapi_app/app/features/internal/fetch_image/router.py

import traceback
from typing import List

from fastapi import APIRouter, HTTPException, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import HttpUrl, ValidationError

from app.core.config import settings

from .schema import ImageFetchResponse
from .service import fetch_and_save_images

router = APIRouter()
api_key_header = APIKeyHeader(name="x-internal-secret", auto_error=True)


def filter_valid_http_urls(image_urls: List[str]) -> List[HttpUrl]:
    try:
        # pydantic이 각 요소를 HttpUrl로 파싱 (검증 실패 시 ValidationError 발생)
        from pydantic import parse_obj_as

        return parse_obj_as(List[HttpUrl], image_urls)
    except ValidationError as e:
        # 유효하지 않은 URL이 섞여 있을 경우 개별 필터링 수행
        valid_urls: List[HttpUrl] = []
        for url in image_urls:
            try:
                valid_urls.append(parse_obj_as(HttpUrl, url))
            except ValidationError:
                continue
        return valid_urls


@router.get("/fetch/image", response_model=ImageFetchResponse, tags=["[Internal] 대표 이미지 수집"])
async def fetch_image_handler(x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    try:
        image_urls = await fetch_and_save_images()
        valid_urls = filter_valid_http_urls(image_urls)
        return ImageFetchResponse(images=valid_urls)

    except Exception:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "대표 이미지 API 호출 중 오류가 발생했습니다."},
        )
