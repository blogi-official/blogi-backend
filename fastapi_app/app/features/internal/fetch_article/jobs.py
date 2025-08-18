# app/features/internal/fetch_article/jobs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Final, Literal, Optional, TypedDict

from app.common.logger import get_logger

# ✅ 배치 종료 시 브라우저/드라이버까지 완전 정리 (선택이지만 권장)
from app.features.internal.fetch_article.scraper.playwright_browser import (
    recycle_browser,
)

# ✅ services의 "원문" 함수를 그대로 사용 (리턴 없음)
from app.features.internal.fetch_article.services import scrape_and_send_articles

logger = get_logger(__name__)

Status = Literal["pending", "running", "done", "failed"]


class JobStatusResponse(TypedDict, total=False):
    status: Status | Literal["not_found"]
    result: Optional[dict]
    error: Optional[str]


@dataclass
class JobData:
    status: Status  # "pending" | "running" | "done" | "failed"
    result: Optional[dict]
    error: Optional[str]


_JOBS: Final[Dict[str, JobData]] = {}


def create_job(job_id: str) -> None:
    """잡 엔트리를 초기화합니다."""
    _JOBS[job_id] = JobData(status="pending", result=None, error=None)
    logger.info(f"[JOB CREATE] {job_id}")


def get_job_status(job_id: str) -> JobStatusResponse:
    """잡 상태를 조회합니다."""
    job = _JOBS.get(job_id)
    if not job:
        return {"status": "not_found"}
    return {"status": job.status, "result": job.result, "error": job.error}


async def run_job(job_id: str) -> None:
    """
    단건 루프형 수집 작업 실행.
    services.scrape_and_send_articles()는 반환값이 없으므로
    완료 시 result에는 간단한 요약만 기록합니다.
    """
    job = _JOBS.get(job_id)
    if not job:
        logger.warning(f"[JOB] not found: {job_id}")
        return
    if job.status == "running":
        logger.warning(f"[JOB] already running: {job_id}")
        return

    job.status = "running"
    job.error = None
    job.result = None
    logger.info(f"[JOB RUN] {job_id}")

    try:
        # ⚙️ 반환값 없음(None). 예외 없이 끝나면 성공으로 처리.
        await scrape_and_send_articles()

        job.status = "done"
        job.result = {"message": "scrape_and_send_articles completed", "ok": True}
        logger.info(f"[JOB DONE] {job_id}")
    except Exception as e:
        job.error = str(e)
        job.status = "failed"
        job.result = {"message": "scrape_and_send_articles failed", "ok": False}
        logger.exception(f"[JOB FAIL] {job_id}: {e}")
    finally:
        # ✅ 배치가 어떻게 끝나든 브라우저/드라이버 완전 종료 (유휴 시 프로세스 잔류 방지)
        try:
            await recycle_browser()
        except Exception:
            pass
