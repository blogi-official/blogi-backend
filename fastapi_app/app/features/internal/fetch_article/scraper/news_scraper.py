from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.common.logger import get_logger
from app.features.internal.fetch_article.scraper.playwright_browser import get_browser
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    DEFAULT_SELECTORS,
    DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 본문 추출
async def extract_news_content(url: str) -> str | None:
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

            logger.info(f"페이지 이동 시도 중: {url}")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            logger.info(f"페이지 이동 성공: {url}")

            domain = urlparse(url).netloc.replace("www.", "")
            selectors = [DOMAIN_SELECTOR_MAP[domain]] if domain in DOMAIN_SELECTOR_MAP else DEFAULT_SELECTORS

            for selector in selectors:
                try:
                    content = await page.inner_text(selector)
                    if content.strip():
                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(
                            f"[본문 추출 성공] selector={selector}, 길이={len(content)} | 내용 미리보기: {preview}..."
                        )
                        await context.close()
                        return content.strip()
                except Exception:
                    continue

            logger.warning(f"[본문 없음] 모든 선택자 실패: {url}")
            await context.close()
            return None

    except Exception as e:
        logger.error(f"[Playwright 전체 실패] {url} - {e}")
        return None
