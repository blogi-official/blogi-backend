#scraper.py
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.common.logger import get_logger

logger = get_logger(__name__)


# requests 기반 본문 추출
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

# 도메인별 selector 매핑
DOMAIN_SELECTOR_MAP = {
    "topstarnews.net": "#dic_area",
    "sedaily.com": "#v-left-scroll-in",
    "esquirekorea.co.kr": ".article-view",
    "xportsnews.com": "#newsContent",
    "edaily.co.kr": "#newsContent",
    "newsen.com": "#news_body_area",
    "doctorsnews.co.kr": "div.view_con",
    # fallback 없이 빈 선택자로 두지 말고, 아래 default_selectors를 쓰도록
}

# 기본 selector 리스트 (매핑 실패 시 사용)
DEFAULT_SELECTORS = ["#dic_area", "article", ".article", ".view", "#articleBodyContents"]

# Playwright 기반 본문 추출 (재시도용)
async def extract_with_playwright(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # 실제 브라우저 띄워서 동작 확인
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale="ko-KR",
                viewport={"width": 1280, "height": 1024},
                permissions=["geolocation"],
                bypass_csp=True,  # 콘텐츠 보안 정책 우회
            )
            page = await context.new_page()

            try:
                logger.info(f"페이지 이동 시도 중: {url}")
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                logger.info(f"페이지 이동 성공: {url}")
            except TimeoutError:
                logger.error(f"[Timeout] 페이지 로딩 실패: {url}")
                return ""
            except Exception as e:
                logger.error(f"[Error] 페이지 이동 실패: {url} - {e}")
                return ""

            domain = urlparse(url).netloc.replace("www.", "")
            selectors = [DOMAIN_SELECTOR_MAP[domain]] if domain in DOMAIN_SELECTOR_MAP else DEFAULT_SELECTORS

            for selector in selectors:
                try:
                    content = await page.inner_text(selector)
                    if content.strip():
                        preview = content.strip()[:100].replace("\n", " ")
                        logger.info(f"[본문 추출 성공] selector={selector}, 길이={len(content)} | 내용 미리보기: {preview}...")
                        return content.strip()
                except Exception:
                    continue  # 선택자 실패 시 다음으로

            logger.warning(f"[본문 없음] 모든 선택자 실패: {url}")
            return ""

            await context.close()  # context만 닫기 (브라우저는 유지)
            return content.strip()

    except Exception as e:
        logger.error(f"[Playwright 전체 실패] {url} - {e}")
        return ""

# 본문이 없거나 짧으면 Playwright 재시도
async def extract_article_content(url: str) -> str:
    content = await extract_with_requests(url)
    if content:
        print(f"[DEBUG] [requests] 성공: {url}")
    else:
        print(f"[DEBUG] [requests] 실패, Playwright 재시도: {url}")

    if not content or len(content) < 100:
        content = await extract_with_playwright(url)
        if content:
            print(f"[DEBUG] [playwright] 성공: {url}")
        else:
            print(f"[DEBUG] [playwright] 실패: {url}")
    return content



