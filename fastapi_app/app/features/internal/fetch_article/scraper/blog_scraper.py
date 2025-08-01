from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.common.logger import get_logger
from app.features.internal.fetch_article.scraper.playwright_browser import get_browser
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    BLOG_DEFAULT_SELECTORS,
    BLOG_DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 블로그 본문 추출
async def extract_blog_content(url: str) -> str | None:
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

            logger.info(f"[블로그] 페이지 이동 시도: {url}")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            logger.info(f"[블로그] 페이지 이동 성공: {url}")

            domain = urlparse(url).netloc.replace("www.", "")
            raw_selector = BLOG_DOMAIN_SELECTOR_MAP.get(domain)

            # 타입 안정성 확보
            if isinstance(raw_selector, str):
                selectors = [raw_selector]
            elif isinstance(raw_selector, list):
                selectors = raw_selector
            else:
                selectors = BLOG_DEFAULT_SELECTORS

            for selector in selectors:
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
            return None

    except Exception as e:
        logger.error(f"[Playwright 블로그 추출 실패] {url} - {e}")
        return None
