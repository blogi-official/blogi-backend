import re
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse


def clean_text(text: str) -> str:
    # zero-width/invisible 문자만 제거 (이모티콘 유지)
    return re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ue000-\uf8ff]", "", text).strip()


# 키워드 제목 정제 (이모티콘은 유지, 날짜는 Asia/Seoul 기준으로 정제)
def clean_raw_data(item: dict) -> dict:
    if "title" in item:
        # 이모티콘 포함한 유니코드 문자 유지, 제로-위드스 문자만 제거
        item["title"] = clean_text(item["title"])

    if "collected_at" in item:
        try:
            dt = isoparse(item["collected_at"])
            item["collected_at"] = dt.astimezone(ZoneInfo("Asia/Seoul")).isoformat()
        except Exception:
            item["collected_at"] = datetime.now(tz=ZoneInfo("Asia/Seoul")).isoformat()

    return item


# 네이버 블로그 전용 본문 정제 함수
def clean_naver_blog_content(content: str) -> str:
    # 여기에 블로그 특유의 광고, 불필요 문구 제거 로직 추가
    # 예시로 간단히 줄바꿈 제거 및 공백 정리
    cleaned = content.replace("\n", " ").strip()
    # 추가 필터링 구현 가능
    return cleaned
