# text_utils.py
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse


def clean_text(text: str) -> str:
    return re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ue000-\uf8ff]", "", text).strip()


# 키워드 특수문자 제거 및 날짜 정제
def clean_raw_data(item: dict) -> dict:
    if "title" in item:
        item["title"] = re.sub(r"[^\w\s가-힣\-\.,]", "", item["title"])

    if "collected_at" in item:
        try:
            dt = isoparse(item["collected_at"])

            item["collected_at"] = dt.astimezone(ZoneInfo("Asia/Seoul")).isoformat()
        except Exception:
            item["collected_at"] = datetime.now(tz=ZoneInfo("Asia/Seoul")).isoformat()

    return item
