from urllib.parse import urlparse

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from app.common.logger import get_logger
from app.features.internal.fetch_article.filtering import (
    is_valid_blog_content,  # 필터링 적용
)
from app.features.internal.fetch_article.scraper.playwright_browser import get_browser
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    BLOG_DEFAULT_SELECTORS,
    BLOG_DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 블로그 본문 추출
async def extract_blog_content(url: str, keyword: str) -> str | None:
    async with async_playwright() as p:
        try:
            # 1차 시도: 모바일 환경
            browser = await get_browser()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
                "Mobile/15E148 Safari/604.1",
                locale="ko-KR",
                viewport={"width": 375, "height": 812},
                permissions=["geolocation"],
                bypass_csp=True,
            )
            page = await context.new_page()

            logger.info(f"[블로그] 모바일 페이지 이동 시도: {url}")
            await page.goto(url, timeout=30000, wait_until="networkidle")

            domain = urlparse(url).netloc.replace("www.", "")
            raw_selector = BLOG_DOMAIN_SELECTOR_MAP.get(domain)
            selectors = (
                [raw_selector]
                if isinstance(raw_selector, str)
                else (raw_selector if isinstance(raw_selector, list) else BLOG_DEFAULT_SELECTORS)
            )

            for selector in selectors:
                if not selector:
                    continue
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    content = await page.inner_text(selector)
                    if content.strip():
                        # 필터링 기준 적용
                        if not is_valid_blog_content(content, keyword):
                            logger.warning(f"[제외됨] 본문 관련성 부족 또는 너무 짧음 → keyword: {keyword}, url: {url}")
                            await context.close()
                            return None

                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(
                            f"[블로그 본문 추출 성공 - 모바일] selector={selector}, 길이={len(content)} | 미리보기: {preview}..."
                        )
                        await context.close()
                        return content.strip()
                except Exception:
                    continue

            logger.warning(f"[블로그 본문 없음 - 모바일] 모든 선택자 실패: {url}")
            await context.close()

            # 2차 시도: PC + iframe
            logger.info(f"[블로그] iframe 접근 시도: {url}")
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 1024},
                locale="ko-KR",
                bypass_csp=True,
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until="networkidle")

            frame = page.frame(name="mainFrame")
            if not frame:
                raise Exception("mainFrame iframe not found.")

            for selector in selectors:
                if not selector:
                    continue
                try:
                    await frame.wait_for_selector(selector, timeout=5000)
                    content = await frame.inner_text(selector)
                    if content.strip():
                        # 필터링 기준 적용
                        if not is_valid_blog_content(content, keyword):
                            logger.warning(f"[제외됨] 본문 관련성 부족 또는 너무 짧음 → keyword: {keyword}, url: {url}")
                            await context.close()
                            return None

                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(
                            f"[블로그 본문 추출 성공 - iframe] selector={selector}, 길이={len(content)} | 미리보기: {preview}..."
                        )
                        await context.close()
                        return content.strip()
                except Exception:
                    continue

            logger.warning(f"[블로그 본문 없음 - iframe] 모든 선택자 실패: {url}")
            await context.close()
            return None

        except Exception as e:
            logger.error(f"[Playwright 블로그 추출 실패] {url} - {e}")
            return None
