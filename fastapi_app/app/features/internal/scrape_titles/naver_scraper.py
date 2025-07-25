import re
from datetime import datetime

from playwright.async_api import async_playwright

from app.features.internal.scrape_titles.config import CATEGORY_MAP


def clean_text(text: str) -> str:
    return re.sub(
        r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ue000-\uf8ff]", "", text
    ).strip()


async def scrape_titles() -> list[dict]:
    result = []

    print("[DEBUG] Playwright 시작 전")

    async with async_playwright() as p:
        print("[DEBUG] Playwright 실행됨")
        browser = await p.chromium.launch(headless=True)
        print("[DEBUG] 브라우저 실행됨")
        page = await browser.new_page()
        print("[DEBUG] 페이지 객체 생성됨")

        for category, display_name in CATEGORY_MAP.items():
            # category_encoded = quote_plus(display_name)
            # query_encoded = quote_plus(query)

            category_encoded = display_name
            query = f"{display_name} 숏텐츠"
            print(query)

            query_encoded = query
            print(query_encoded)

            url = (
                f"https://search.naver.com/search.naver?"
                f"category={category_encoded}&query={query_encoded}"
                f"&sm=svc_clk.entnewsmore&ssc=tab.shortents.all"
            )
            print(f"[DEBUG] 카테고리: {category}, URL: {url}")

            try:
                await page.goto(url, timeout=10000)
                print(f"[DEBUG] {category} 페이지 이동 완료")

                # TODO: 맛집분야 했지만 기사로 바꾸기. 전체를 확인하는 코드로 수정 혹은 카테고리별로 map로 하기
                titles = await page.eval_on_selector_all(
                    "span.sds-comps-text-type-headline2",
                    "elements => elements.map(el => el.innerText)",
                )

                print(f"[DEBUG] {category} 제목 수집 완료, 개수: {len(titles)}")

                for t in titles:
                    result.append(
                        {
                            "title": clean_text(t),
                            "category": category,
                            "source": "네이버",
                            "collected_at": datetime.utcnow().isoformat(),
                        }
                    )
                print(f"[스크래핑 결과] {category} 카테고리 → {len(titles)}개 수집됨")

            except Exception as e:
                print(f"[ERROR] Failed to scrape {category}: {e}")

        await browser.close()
        print(f"[총 수집 결과] 총 키워드 {len(result)}개 수집 완료")

    # 📌 여기에 결과 리스트 출력 추가
    for item in result:
        print(f"[수집된 제목] {item['category']} - {item['title']}")

    return result
