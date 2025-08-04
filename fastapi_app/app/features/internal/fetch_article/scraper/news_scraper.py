from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.common.logger import get_logger
from app.features.internal.fetch_article.filtering import (  # 필터 추가
    is_valid_blog_content,
)
from app.features.internal.fetch_article.scraper.playwright_browser import get_browser
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    DEFAULT_SELECTORS,
    DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 뉴스 본문 추출
async def extract_news_content(url: str, keyword: str) -> str | None:
    try:
        async with async_playwright() as p:
            browser = await get_browser()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
                "Mobile/15E148 Safari/604.1",  #  모바일 UA 적용
                locale="ko-KR",
                viewport={"width": 375, "height": 812},
                permissions=["geolocation"],
                bypass_csp=True,
            )
            page = await context.new_page()

            logger.info(f"[뉴스] 모바일 페이지 이동 시도 중: {url}")
            await page.goto(url, timeout=30000, wait_until="networkidle")
            logger.info(f"[뉴스] 페이지 이동 성공: {url}")

            domain = urlparse(url).netloc.replace("www.", "")
            selectors = [DOMAIN_SELECTOR_MAP[domain]] if domain in DOMAIN_SELECTOR_MAP else DEFAULT_SELECTORS

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    content = await page.inner_text(selector)
                    if content.strip():
                        # 필터링 기준 적용
                        if not is_valid_blog_content(content, keyword):
                            logger.warning(
                                f"[제외됨] 뉴스 본문 관련성 부족 또는 너무 짧음 → keyword: {keyword}, url: {url}"
                            )
                            await context.close()
                            return None

                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(
                            f"[뉴스 본문 추출 성공] selector={selector}, 길이={len(content)} | 미리보기: {preview}..."
                        )
                        await context.close()
                        return content.strip()
                except Exception:
                    continue

            logger.warning(f"[뉴스 본문 없음] 모든 선택자 실패: {url}")
            await context.close()
            return None

    except Exception as e:
        logger.error(f"[Playwright 뉴스 추출 실패] {url} - {e}")
        return None
