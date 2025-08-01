import asyncio
from typing import Dict, Union

import httpx

from app.common.logger import get_logger
from app.common.utils.text_utils import clean_encoded_text
from app.core.config import settings

logger = get_logger(__name__)


def fix_url_protocol(url: str) -> str:
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # 자주 나오는 오타 보정
    if url.startswith("htt://"):
        return "http://" + url[6:]
    if url.startswith("hps://"):
        return "https://" + url[6:]
    if url.startswith("httpog://"):
        return "http://" + url[8:]
    # 이 외에는 https:// 붙이기
    return "https://" + url.lstrip("/:")


async def search_news(query: str, type: str = "news", display: int = 3):
    if type == "news":
        url = "https://openapi.naver.com/v1/search/news.json"
        params = {
            "query": query,
            "display": display,
            "start": 1,
            "sort": "date",
        }

    elif type == "blog":
        url = "https://openapi.naver.com/v1/search/blog.json"
        params = {
            "query": query,
            "display": display,
            "start": 1,
            "sort": "sim",
        }
    else:
        raise ValueError("Invalid type")

    headers = {
        "X-Naver-Client-Id": settings.naver_client_id,
        "X-Naver-Client-Secret": settings.naver_client_secret,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)  # type: ignore
            logger.debug(f"네이버 API 원본 응답: {response.text}")

            if response.status_code != 200:
                raise Exception(f"네이버 API 검색 실패, status_code={response.status_code}")

            data = response.json()
            items = data.get("items", [])
            logger.info(f"search_news - query: {query}, type: {type}, items count: {len(items)}")
            for i, item in enumerate(items):
                logger.info(f"item {i}: {item}")

            for item in items:
                raw_title = item.get("title", "")
                raw_description = item.get("description", "")
                raw_link = item.get("link", "")
                blogger_link = item.get("bloggerlink", "")
                postdate = item.get("postdate", "")

                clean_title = clean_encoded_text(raw_title)
                clean_description = clean_encoded_text(raw_description)

                # raw_link가 http/https로 시작하지 않으면 보정 시도
                if not raw_link.startswith("http"):
                    logger.warning(f"잘못된 link 값 발견: {raw_link} - 원본 item: {item}")
                    raw_link = fix_url_protocol(raw_link)

                # origin_link 조합
                origin_link = ""
                if blogger_link and raw_link:
                    blogger_id = blogger_link.split("/")[-1]
                    # raw_link에서 게시글 번호만 추출 (마지막 슬래시 뒤)
                    post_num = raw_link.rstrip("/").split("/")[-1]
                    try:
                        post_num = raw_link.rstrip("/").split("/")[-1]
                        origin_link = f"https://blog.naver.com/{blogger_id}/{post_num}"
                    except Exception:
                        # post_num 추출 실패시 그냥 blogger_link만 사용
                        origin_link = fix_url_protocol(blogger_link)
                else:
                    origin_link = raw_link

                # origin_link 다시 보정 함수 한번 더 통과시키기 (필요 시)
                origin_link = fix_url_protocol(origin_link)

                item["clean_title"] = clean_title
                item["clean_description"] = clean_description
                item["origin_link"] = origin_link

                logger.info(f"제목: {clean_title}")
                logger.info(f"설명: {clean_description}")
                logger.info(f"origin_link 조합: {origin_link}")
                logger.info(f"postdate: {postdate}")

            return items
    except asyncio.CancelledError:
        print(f"search_news 작업이 취소되었습니다. query={query}")
        raise
    except Exception as e:
        print(f"search_news 에러 발생: {e}")
        raise
