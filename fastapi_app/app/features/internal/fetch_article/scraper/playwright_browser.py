# app/features/internal/fetch_article/scraper/playwright_browser.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Tuple

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

_pw = None
_browser: Optional[Browser] = None


async def get_browser() -> Browser:
    """
    싱글턴 브라우저 반환. 최초 1회만 런치.
    """
    global _pw, _browser
    if _browser is None:
        _pw = await async_playwright().start()
        _browser = await _pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--media-cache-size=0",
                "--disk-cache-size=0",
                "--disable-background-networking",
                "--no-first-run",
                "--no-zygote",
            ],
        )
    return _browser


async def close_all_contexts() -> None:
    """
    열려 있는 모든 컨텍스트를 안전하게 닫음.
    """
    global _browser
    if not _browser:
        return
    for ctx in list(_browser.contexts):
        try:
            await ctx.close()
        except Exception:
            # 이미 닫혔거나, 일시적 에러는 무시
            pass


async def recycle_browser() -> None:
    """
    브라우저/드라이버 완전 종료. 다음 get_browser() 호출 시 재생성.
    """
    global _pw, _browser
    await close_all_contexts()
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


@asynccontextmanager
async def context(**kwargs) -> AsyncGenerator[BrowserContext, None]:
    """
    호출부 호환용 컨텍스트 매니저 (BrowserContext만 yield).
    사용 예:
        async with context(user_agent="...") as ctx:
            page = await ctx.new_page()
            ...
    """
    browser = await get_browser()
    ctx: BrowserContext = await browser.new_context(**kwargs)
    try:
        yield ctx
    finally:
        try:
            await ctx.close()
        except Exception:
            pass


@asynccontextmanager
async def new_context(**kwargs) -> AsyncGenerator[Tuple[BrowserContext, Page], None]:
    """
    컨텍스트 + 페이지를 함께 제공하는 헬퍼.
    사용 예:
        async with new_context(user_agent="...") as (ctx, page):
            await page.goto(url)
            ...
    """
    browser = await get_browser()
    ctx: BrowserContext = await browser.new_context(**kwargs)
    page: Page = await ctx.new_page()
    try:
        yield ctx, page
    finally:
        # 페이지 → 컨텍스트 순으로 안전 종료
        try:
            await page.close()
        except Exception:
            pass
        try:
            await ctx.close()
        except Exception:
            pass
