from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from playwright.async_api import Browser, BrowserContext, async_playwright

# 동시 처리 제한 (환경변수로 조절 가능, 기본 3)
MAX_CONCURRENCY = int(os.getenv("PLAYWRIGHT_MAX_CONCURRENCY", "3"))

_pw = None
_browser: Optional[Browser] = None
_sem = asyncio.Semaphore(MAX_CONCURRENCY)
_lock = asyncio.Lock()

LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--media-cache-size=0",
    "--disk-cache-size=0",
]


async def get_browser() -> Browser:
    """싱글 브라우저 반환. 없으면 생성."""
    global _pw, _browser
    async with _lock:
        if _browser is None:
            _pw = await async_playwright().start()
            _browser = await _pw.chromium.launch(headless=True, args=LAUNCH_ARGS)
        return _browser


@asynccontextmanager
async def context(**kwargs) -> AsyncGenerator[BrowserContext, None]:
    """
    컨텍스트 컨텍스트매니저.
    - 세마포어로 동시성 제한
    - kwargs는 new_context(...)로 그대로 전달
    - 이미지/폰트/미디어 차단(부하 절감)
    """
    browser = await get_browser()
    async with _sem:
        ctx = await browser.new_context(**kwargs)
        await ctx.route(
            "**/*",
            lambda route: (
                route.abort() if route.request.resource_type in {"image", "media", "font"} else route.continue_()
            ),
        )
        try:
            yield ctx
        finally:
            try:
                await ctx.close()
            except Exception:
                pass


async def shutdown() -> None:
    """서버 종료 시 정리."""
    global _pw, _browser
    async with _lock:
        if _browser:
            try:
                await _browser.close()
            except Exception:
                pass
            _browser = None
        if _pw:
            try:
                await _pw.stop()
            except Exception:
                pass
            _pw = None
