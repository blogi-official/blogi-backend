from urllib.parse import urlparse

from playwright.async_api import BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.common.logger import get_logger
from app.features.internal.fetch_article.filtering import is_valid_blog_content
from app.features.internal.fetch_article.scraper.playwright_browser import (
    context as browser_context,  # 기존 컨텍스트 매니저 그대로 사용
)
from app.features.internal.fetch_article.scraper.playwright_selectors import (
    BLOG_DEFAULT_SELECTORS,
    BLOG_DOMAIN_SELECTOR_MAP,
)

logger = get_logger(__name__)


# Playwright 기반 블로그 본문 추출 (누수 방지 보강판)
async def extract_blog_content(url: str, keyword: str) -> str | None:
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        raw_selector = BLOG_DOMAIN_SELECTOR_MAP.get(domain)
        selectors = (
            [raw_selector]
            if isinstance(raw_selector, str)
            else (raw_selector if isinstance(raw_selector, list) else BLOG_DEFAULT_SELECTORS)
        )

        # --------------------------------------------------------------------------------------------------
        # 1차: 모바일 렌더링 시도
        # --------------------------------------------------------------------------------------------------
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
                logger.info(f"[블로그] 모바일 페이지 이동 시도: {url}")
                # networkidle 실패 시 domcontentloaded로 폴백 (불필요 대기 줄임)
                try:
                    await page.goto(url, timeout=30000, wait_until="networkidle")
                except PlaywrightTimeoutError:
                    logger.warning("[블로그] 모바일 networkidle 타임아웃 → domcontentloaded 폴백")
                    await page.goto(url, timeout=15000, wait_until="domcontentloaded")

                for selector in selectors:
                    if not selector:
                        continue
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        content = await page.inner_text(selector)
                        if content and content.strip():
                            if not is_valid_blog_content(content, keyword):
                                logger.warning(f"[제외됨] 관련성 부족/너무 짧음 → keyword={keyword}, url={url}")
                                return None
                            preview = content.strip()[:100].replace("\n", " ")
                            logger.info(
                                f"[블로그 본문 추출 성공-모바일] selector={selector}, len={len(content)} | {preview}..."
                            )
                            return content.strip()
                    except PlaywrightTimeoutError:
                        continue
                    except Exception:
                        continue

                logger.warning(f"[블로그 본문 없음-모바일] 모든 선택자 실패: {url}")
            finally:
                # ✅ 페이지 핸들 항상 정리 (컨텍스트는 async with가 정리)
                try:
                    await page.close()
                except Exception:
                    pass

        # --------------------------------------------------------------------------------------------------
        # 2차: PC + iframe(mainFrame) 시도
        # --------------------------------------------------------------------------------------------------
        async with browser_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 1024},
            locale="ko-KR",
            bypass_csp=True,
        ) as ctx:  # type: BrowserContext
            page = await ctx.new_page()
            try:
                logger.info(f"[블로그] iframe 접근 시도: {url}")
                # 마찬가지로 폴백
                try:
                    await page.goto(url, timeout=30000, wait_until="networkidle")
                except PlaywrightTimeoutError:
                    logger.warning("[블로그] PC networkidle 타임아웃 → domcontentloaded 폴백")
                    await page.goto(url, timeout=15000, wait_until="domcontentloaded")

                # frame 탐색(이름, 부분일치 폴백) → 없으면 메인 페이지로 폴백
                frame = page.frame(name="mainFrame") or next(
                    (f for f in page.frames if (f.name or "").lower().find("mainframe") >= 0),
                    None,
                )
                target = frame if frame else page
                if not frame:
                    logger.warning("[블로그] mainFrame 미발견 → main page에서 직접 추출 시도")

                for selector in selectors:
                    if not selector:
                        continue
                    try:
                        await target.wait_for_selector(selector, timeout=5000)
                        # frame이면 frame.inner_text, 아니면 page.inner_text
                        content = await (target.inner_text(selector) if frame else page.inner_text(selector))
                        if content and content.strip():
                            if not is_valid_blog_content(content, keyword):
                                logger.warning(f"[제외됨] 관련성 부족/너무 짧음 → keyword={keyword}, url={url}")
                                return None
                            preview = content.strip()[:100].replace("\n", " ")
                            hit_from = "iframe" if frame else "page"
                            logger.info(
                                f"[블로그 본문 추출 성공-{hit_from}] selector={selector}, len={len(content)} | {preview}..."
                            )
                            return content.strip()
                    except PlaywrightTimeoutError:
                        continue
                    except Exception:
                        continue

                logger.warning(f"[블로그 본문 없음-iframe] 모든 선택자 실패: {url}")
                return None

            finally:
                # ✅ 페이지 핸들 항상 정리
                try:
                    await page.close()
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"[Playwright 블로그 추출 실패] {url} - {e}")
        return None
