# app/utils/playwright_browser.py

from playwright.async_api import async_playwright

_browser = None

async def get_browser():
    global _browser
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=True)  # headless=True로 설정
    return _browser
