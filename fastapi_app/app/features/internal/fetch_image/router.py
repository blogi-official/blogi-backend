# fastapi_app/app/features/internal/fetch_image/router.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .schema import ImageFetchResponse
from .service import fetch_and_save_images

router = APIRouter()


@router.get("/fetch/image", response_model=ImageFetchResponse, tags=["[Internal] 대표 이미지 수집"])
async def fetch_image_handler():
    try:
        image_urls = await fetch_and_save_images()
        return ImageFetchResponse(images=image_urls)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "대표 이미지 API 호출 중 오류가 발생했습니다."},
        )
