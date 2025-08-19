# time_utils.py
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse

from app.common.logger import get_logger

logger = get_logger(__name__)


# ISO 날짜 형식이 아닐 경우 현재 시각으로 대체
def parse_collected_at(raw_date_str: str) -> str:
    try:
        dt = isoparse(raw_date_str)
        return dt.astimezone(ZoneInfo("Asia/Seoul")).isoformat()
    except Exception as e:
        logger.warning(f"날짜 변환 실패, 기본값 사용: {raw_date_str}, 에러: {e}")
        return datetime.now(tz=ZoneInfo("Asia/Seoul")).isoformat()
