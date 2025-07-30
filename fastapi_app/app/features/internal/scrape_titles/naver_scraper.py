import asyncio
import re
from datetime import datetime, timezone

from playwright.async_api import async_playwright

from app.common.logger import get_logger
from app.common.utils.text_utils import clean_text
from app.features.internal.scrape_titles.config import CATEGORY_MAP

logger = get_logger(__name__)


# 각 카테고리에 대해 네이버 검색에서 제목(키워드) 리스트 수집
async def scrape_titles() -> list[dict]:
    result = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for category, display_name in CATEGORY_MAP.items():
            query = f"{display_name} 숏텐츠"

            url = (
                f"https://search.naver.com/search.naver?"
                f"category={display_name}&query={query}"
                f"&sm=svc_clk.entnewsmore&ssc=tab.shortents.all"
            )

            # 수집된 제목 리스트에 추가
            try:
                await page.goto(url, timeout=10000)

                titles = await page.eval_on_selector_all(
                    "span.sds-comps-text-type-headline2",
                    "elements => elements.map(el => el.innerText)",
                )

                for t in titles:
                    result.append(
                        {
                            "title": clean_text(t),
                            "category": category,
                            "source_category": display_name,
                            "collected_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                        }
                    )

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Failed to scrape {category}: {e}", exc_info=True)

        await browser.close()

    return result
