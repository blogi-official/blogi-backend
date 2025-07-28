# scraper.py
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def extract_with_requests(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.select_one("#dic_area")  # 네이버 뉴스 본문
        return content_div.get_text(strip=True) if content_div else ""
    except Exception:
        return ""


async def extract_with_playwright(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=15000)
            content = await page.inner_text("#dic_area")
            await browser.close()
            return content.strip()
    except Exception:
        return ""


async def extract_article_content(url: str) -> str:
    content = await extract_with_requests(url)
    if not content or len(content) < 100:
        content = await extract_with_playwright(url)
    return content
