# fastapi_app/app/common/scheduler.py
from __future__ import annotations

import asyncio
import random
import time
import uuid
from typing import Any, Awaitable, Callable, Optional

import app.features.internal.fetch_article.jobs as article_jobs  # 기사 수집 (jobs)
from app.common.logger import get_logger
from app.features.internal.fetch_image.service import (  # 이미지 수집
    fetch_and_save_images,
)

# === 우리 프로젝트 실제 경로 ===
from app.features.internal.scrape_titles.services import (
    fetch_and_send_to_django,  # 키워드 수집
)

logger = get_logger(__name__)

# 운영에서 바꾸고 싶으면 os.getenv로 치환 가능
INITIAL_DELAY_SECONDS = 180  # 서버 기동 안전 대기 3분
INTERVAL_SECONDS = 6 * 60 * 60  # 6시간
JITTER_SECONDS = 30  # 사이클 시작 전 0~30초 랜덤 지연

AsyncNoArg = Callable[[], Awaitable[None]]

_lock: Optional[asyncio.Lock] = None
_first_run_done = False


async def _to_async(fn: Callable[..., Any], *args, **kwargs):
    """동기/비동기 함수 모두 안전 호출."""
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return await asyncio.to_thread(lambda: fn(*args, **kwargs))


def _wrap_noarg(fn: Callable[..., Any]) -> AsyncNoArg:
    async def _runner() -> None:
        await _to_async(fn)

    return _runner


# === 단계 실행 함수 (우리 실제 구현에 맞춤) ===
keyword_step: AsyncNoArg = _wrap_noarg(fetch_and_send_to_django)


async def article_step() -> None:
    """
    ✅ 우리 jobs 구현에 맞춰 정확히 실행:
    1) job_id 생성 → 2) jobs.create_job(job_id) → 3) jobs.run_job(job_id)
    """
    job_id = uuid.uuid4().hex
    logger.info(f"[Scheduler] article(job) create: job_id={job_id}")
    await _to_async(article_jobs.create_job, job_id)  # ← 반드시 먼저 등록
    logger.info(f"[Scheduler] article(job) start: job_id={job_id}")
    await _to_async(article_jobs.run_job, job_id)  # ← 등록된 id로 실행


image_step: AsyncNoArg = _wrap_noarg(fetch_and_save_images)


async def _initial_wait():
    if INITIAL_DELAY_SECONDS > 0:
        logger.info(f"[Scheduler] initial safety wait: {INITIAL_DELAY_SECONDS}s")
        try:
            await asyncio.sleep(INITIAL_DELAY_SECONDS)
        except asyncio.CancelledError:
            return


async def _jitter_wait():
    if JITTER_SECONDS > 0:
        j = random.randint(0, JITTER_SECONDS)
        if j:
            logger.info(f"[Scheduler] jitter before cycle: {j}s")
            try:
                await asyncio.sleep(j)
            except asyncio.CancelledError:
                return


async def run_cycle_once() -> None:
    """키워드 → 기사(job) → 이미지 한 번 실행 (중복 방지 락 포함)."""
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()

    if _lock.locked():
        logger.warning("[Scheduler] previous cycle still running. Skip this tick.")
        return

    async with _lock:
        started = time.time()
        logger.info("[Scheduler] cycle start: keyword -> article(job) -> image")

        # 1) 키워드
        try:
            await keyword_step()
            logger.info("[Scheduler] keyword step done")
        except Exception:
            logger.exception("[Scheduler] keyword step failed")

        # 2) 기사 (jobs.create_job → jobs.run_job)
        try:
            await article_step()
            logger.info("[Scheduler] article(job) step done")
        except Exception:
            logger.exception("[Scheduler] article(job) step failed")

        # 3) 이미지
        try:
            await image_step()
            logger.info("[Scheduler] image step done")
        except Exception:
            logger.exception("[Scheduler] image step failed")

        logger.info(f"[Scheduler] cycle end (elapsed={time.time() - started:.1f}s)")


async def _sleep_or_kick(kick_evt: asyncio.Event, stop_evt: asyncio.Event, timeout: float):
    # INTERVAL 동안 대기하다가, run_now() 호출로 kick되면 즉시 깨움
    kick_task = asyncio.create_task(kick_evt.wait())
    stop_task = asyncio.create_task(stop_evt.wait())
    try:
        done, pending = await asyncio.wait({kick_task, stop_task}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        if kick_task in done:
            kick_evt.clear()
        for p in pending:
            p.cancel()
    except Exception:
        for p in (kick_task, stop_task):
            if not p.done():
                p.cancel()


class BlogiScheduler:
    """우리 공정 전용 스케줄러 (키워드 → 기사(job) → 이미지, 6시간 간격)."""

    _instance: "BlogiScheduler"

    def __init__(self, name: str = "blogi-scheduler") -> None:
        self.name = name
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._kick_event = asyncio.Event()  # run_now 트리거
        self._paused = False  # 일시정지 플래그
        self._current_task: Optional[asyncio.Task] = None
        BlogiScheduler._instance = self

    # ---- 외부 제어용 메서드 ----
    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._loop(), name=self.name)
        logger.info("[Scheduler] started")

    async def shutdown(self) -> None:
        await self.stop_now(immediate=True)

    def pause(self) -> None:
        self._paused = True
        logger.info("[Scheduler] paused")

    def resume(self) -> None:
        self._paused = False
        self._kick_event.set()
        logger.info("[Scheduler] resumed")

    async def run_now(self) -> None:
        self._kick_event.set()
        logger.info("[Scheduler] run_now requested")

    async def stop_now(self, immediate: bool = False) -> None:
        self._stop_event.set()
        if immediate:
            await self.cancel_running_step()
        if self._task and not self._task.done():
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
        logger.info("[Scheduler] stopped")

    async def cancel_running_step(self) -> bool:
        t = self._current_task
        if t and not t.done():
            logger.info("[Scheduler] cancelling current step...")
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                logger.info("[Scheduler] current step cancelled")
                return True
        return False

    def status(self) -> dict:
        running = self._task is not None and not self._task.done()
        current = None
        if self._current_task:
            current = getattr(self._current_task, "get_name", lambda: None)()
        return {"running": running, "paused": self._paused, "current_task": current}

    # ---- 내부 루프 ----
    async def _loop(self):
        global _first_run_done
        if not _first_run_done:
            await _initial_wait()
            _first_run_done = True

        while not self._stop_event.is_set():
            while self._paused and not self._stop_event.is_set():
                await asyncio.sleep(0.2)

            await _jitter_wait()
            if self._stop_event.is_set():
                break

            # 한 사이클 실행(각 단계는 개별 Task로 실행 → 중간 취소 가능)
            for step_fn, name in (
                (keyword_step, "keyword"),
                (article_step, "article(job)"),
                (image_step, "image"),
            ):
                if self._stop_event.is_set() or self._paused:
                    logger.info(f"[Scheduler] skip step: {name} (stop/pause)")
                    break
                task = asyncio.create_task(step_fn(), name=f"{self.name}:{name}")
                self._current_task = task
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"[Scheduler] step cancelled: {name}")
                    break
                finally:
                    self._current_task = None

            if self._stop_event.is_set():
                break

            await _sleep_or_kick(self._kick_event, self._stop_event, INTERVAL_SECONDS)
