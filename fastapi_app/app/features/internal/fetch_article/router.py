import asyncio
import traceback
import uuid

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.features.internal.fetch_article.jobs import create_job, get_job_status, run_job
from app.features.internal.fetch_article.services import scrape_and_send_articles

fetch_article_router = APIRouter(prefix="/fetch", tags=["Article - Scraper"])
api_key_header = APIKeyHeader(name="x-internal-secret", auto_error=True)


@fetch_article_router.get("/article/")
async def get_article(x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")
    try:
        return await scrape_and_send_articles()
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="네이버 페이지 파싱 중 오류가 발생했습니다.")


# ✅ 잡 시작(즉시 job_id 반환)
@fetch_article_router.post("/article/job")
async def start_article_job(x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")
    job_id = uuid.uuid4().hex
    create_job(job_id)
    asyncio.create_task(run_job(job_id))  # 백그라운드 실행
    return {"job_id": job_id, "status": "pending"}


# ✅ 잡 상태 조회
@fetch_article_router.get("/article/job/{job_id}")
async def get_article_job_status(job_id: str, x_internal_secret: str = Security(api_key_header)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal secret")
    return get_job_status(job_id)
