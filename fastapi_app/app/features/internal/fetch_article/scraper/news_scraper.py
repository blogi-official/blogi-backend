from urllib.parse import urlparse

from playwright.async_api import BrowserContext  # 타입 임포트

from app.common.logger import get_logger
from app.features.internal.fetch_article.filtering import is_valid_blog_content
from app.features.internal.fetch_article.scraper.playwright_browser import (
    context as browser_context,
)
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    DEFAULT_SELECTORS,
    DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 뉴스 본문 추출
async def extract_news_content(url: str, keyword: str) -> str | None:
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        selectors = [DOMAIN_SELECTOR_MAP[domain]] if domain in DOMAIN_SELECTOR_MAP else DEFAULT_SELECTORS

        async with browser_context(
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
                "Mobile/15E148 Safari/604.1"
            ),
            locale="ko-KR",
            viewport={"width": 375, "height": 812},
            permissions=["geolocation"],
            bypass_csp=True,
        ) as ctx:  # type: BrowserContext
            page = await ctx.new_page()
            try:
                logger.info(f"[뉴스] 모바일 페이지 이동 시도: {url}")
                await page.goto(url, timeout=30000, wait_until="networkidle")
                logger.info(f"[뉴스] 페이지 이동 성공: {url}")

                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        content = await page.inner_text(selector)
                        if content.strip():
                            if not is_valid_blog_content(content, keyword):
                                logger.warning(f"[제외됨] 뉴스 본문 관련성 부족/짧음 → keyword={keyword}, url={url}")
                                return None
                            preview = content.strip()[:100].replace("\n", " ")
                            logger.info(f"[뉴스 본문 추출 성공] selector={selector}, len={len(content)} | {preview}...")
                            return content.strip()
                    except Exception:
                        continue

                logger.warning(f"[뉴스 본문 없음] 모든 선택자 실패: {url}")
                return None
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"[Playwright 뉴스 추출 실패] {url} - {e}")
        return None
