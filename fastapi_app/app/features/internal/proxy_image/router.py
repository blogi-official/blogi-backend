# app/features/internal/proxy_image/router.py

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse

router = APIRouter()


@router.get("/proxy-image")
async def proxy_image(url: str = Query(..., description="이미지 원본 URL")):
    print(f"[proxy_image] 요청 URL: {url}")  # 디버깅 출력
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            print(f"[proxy_image] 응답 성공: {response.status_code}")
            return StreamingResponse(
                response.aiter_bytes(),
                media_type=response.headers.get("Content-Type", "image/jpeg"),
            )
    except Exception as e:
        print(f"[proxy_image] 요청 실패: {e}")
        raise HTTPException(status_code=500, detail=f"이미지 로딩 실패: {e}")


#  OPTIONS 핸들러 추가
@router.options("/proxy-image")
async def proxy_image_options():
    return Response(status_code=200)
