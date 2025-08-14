# fastapi_app/app/api/v1/scheduler_admin.py
import os

from fastapi import APIRouter, Header, HTTPException
from fastapi import status as http_status  # ✅ alias로 변경

from app.common.scheduler import BlogiScheduler

router = APIRouter(prefix="/admin/scheduler", tags=["admin:scheduler"])

ENV = os.getenv("ENV", "local")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET_KEY", "")  # 기존 내부 인증 키 재사용


def _auth(x_internal_secret: str | None):
    """
    운영(ENV=production)에서는 INTERNAL_SECRET_KEY 반드시 필요.
    비운영에선 설정돼 있으면 검사, 없으면 통과.
    """
    if ENV == "production":
        if not INTERNAL_SECRET:
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler admin disabled: missing INTERNAL_SECRET_KEY",
            )
        if x_internal_secret != INTERNAL_SECRET:
            raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    else:
        # 개발/로컬: INTERNAL_SECRET이 설정돼 있다면 검사, 없으면 프리패스
        if INTERNAL_SECRET and x_internal_secret != INTERNAL_SECRET:
            raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@router.get("/status")
def status(x_internal_secret: str | None = Header(default=None, alias="X-INTERNAL-SECRET")):
    _auth(x_internal_secret)
    return BlogiScheduler._instance.status()


@router.post("/pause")
def pause(x_internal_secret: str | None = Header(default=None, alias="X-INTERNAL-SECRET")):
    _auth(x_internal_secret)
    BlogiScheduler._instance.pause()
    return {"ok": True}


@router.post("/resume")
def resume(x_internal_secret: str | None = Header(default=None, alias="X-INTERNAL-SECRET")):
    _auth(x_internal_secret)
    BlogiScheduler._instance.resume()
    return {"ok": True}


@router.post("/run-now")
async def run_now(x_internal_secret: str | None = Header(default=None, alias="X-INTERNAL-SECRET")):
    _auth(x_internal_secret)
    await BlogiScheduler._instance.run_now()
    return {"ok": True}


@router.post("/cancel-running")
async def cancel_running(
    x_internal_secret: str | None = Header(default=None, alias="X-INTERNAL-SECRET"),
):
    _auth(x_internal_secret)
    cancelled = await BlogiScheduler._instance.cancel_running_step()
    return {"cancelled": cancelled}
