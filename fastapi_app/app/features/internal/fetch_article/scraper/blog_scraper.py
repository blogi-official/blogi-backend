from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.common.constants.scraper_selectors import (
    BLOG_DEFAULT_SELECTORS,
    BLOG_DOMAIN_SELECTOR_MAP,
)
from app.common.logger import get_logger
from app.features.internal.fetch_article.scraper.playwright_browser import get_browser

logger = get_logger(__name__)


async def extract_blog_with_requests(url: str) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # 4xx, 5xx 응답 예외 발생

        soup = BeautifulSoup(response.text, "html.parser")

        for selector in BLOG_DEFAULT_SELECTORS:
            content_div = soup.select_one(selector)
            if content_div:
                text = content_div.get_text(strip=True)
                if text:
                    preview = text[:100].replace("\n", " ")
                    logger.debug(f"[requests] 본문 추출 성공 (selector={selector}): {preview}...")
                    return text

        logger.debug(f"[requests] 모든 selector에서 본문 추출 실패: {url}")
        return ""

    except httpx.HTTPStatusError as e:
        logger.warning(f"[requests] HTTP 오류: {url} - {e.response.status_code}")
        return ""
    except Exception as e:
        logger.debug(f"[requests] 블로그 본문 추출 예외 발생: {url} - {e}")
        return ""


async def extract_blog_with_playwright(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await get_browser()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale="ko-KR",
                viewport={"width": 1280, "height": 1024},
                permissions=["geolocation"],
                bypass_csp=True,
            )
            page = await context.new_page()

            logger.info(f"블로그 페이지 이동 시도 중: {url}")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            logger.info(f"블로그 페이지 이동 성공: {url}")

            domain = urlparse(url).netloc.replace("www.", "")
            selectors = BLOG_DOMAIN_SELECTOR_MAP.get(domain)
            if not selectors:
                selectors = BLOG_DEFAULT_SELECTORS  # type: ignore
            elif isinstance(selectors, str):
                selectors = [selectors]  # type: ignore

            for selector in selectors:  # type: ignore
                if not selector:
                    continue
                try:
                    content = await page.inner_text(selector)
                    if content.strip():
                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(
                            f"[블로그 본문 추출 성공] selector={selector}, 길이={len(content)} | 내용 미리보기: {preview}..."
                        )
                        await context.close()
                        return content.strip()
                except Exception:
                    continue

            logger.warning(f"[블로그 본문 없음] 모든 선택자 실패: {url}")
            await context.close()
            return ""

    except Exception as e:
        logger.error(f"[Playwright 블로그 본문 추출 실패] {url} - {e}")
        return ""


async def extract_blog_content(url: str) -> str:
    logger.info(f"extract_blog_content 시작: {url}")
    content = await extract_blog_with_requests(url)
    if content and len(content) >= 100:
        logger.debug(f"[requests] 블로그 본문 추출 성공: {url}")
        return content

    logger.debug(f"[requests] 블로그 본문 추출 실패 또는 짧음, Playwright 재시도: {url}")
    content = await extract_blog_with_playwright(url)
    if content:
        logger.debug(f"[playwright] 블로그 본문 추출 성공: {url}")
    else:
        logger.debug(f"[playwright] 블로그 본문 추출 실패: {url}")
    return content
