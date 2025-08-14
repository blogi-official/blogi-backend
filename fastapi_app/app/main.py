# fastapi_app/app/main.py
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.common.scheduler import BlogiScheduler
from app.features.internal.fetch_article.scraper.playwright_browser import (
    get_browser,  # 서버 기동 시 예열(선택)
)
from app.features.internal.fetch_article.scraper.playwright_browser import (
    shutdown as pw_shutdown,  # 서버 종료 시 정리
)

# 배포 경로 기준 (필요 시 조정)
# - 로컬에서는 .local.env를 사용하고, 프로드는 .prod.env를 사용하는 구조라면
#   아래 경로를 환경에 맞게 유지/수정하세요.
load_dotenv("/app/envs/.prod.env")

IS_PROD = os.getenv("ENV") == "production"
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
PLAYWRIGHT_PREWARM = os.getenv("PLAYWRIGHT_PREWARM", "true").lower() == "true"

if IS_PROD:
    app = FastAPI(
        root_path="/fastapi",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
else:
    app = FastAPI()

# 라우터
app.include_router(api_router)

# 스케줄러 인스턴스
_scheduler = BlogiScheduler()


@app.on_event("startup")
async def _on_startup():
    # (선택) 브라우저 예열: 첫 호출 지연 및 첫 런치 중 에러를 조기 표면화
    if PLAYWRIGHT_PREWARM:
        try:
            await get_browser()
        except Exception:
            # 예열 실패해도 서버 기동은 진행 (로그는 내부에서 남음)
            pass

    if SCHEDULER_ENABLED:
        await _scheduler.start()


@app.on_event("shutdown")
async def _on_shutdown():
    # 스케줄러 먼저 정지
    try:
        await _scheduler.shutdown()
    except Exception:
        pass

    # Playwright 브라우저/핸들 정리
    try:
        await pw_shutdown()
    except Exception:
        pass


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}


@app.get("/health")
def health():
    return {"ok": True}
