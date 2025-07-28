from datetime import datetime

from pydantic import BaseModel


class ScrapedKeyword(BaseModel):
    title: str
    category: str
    source_category: str
    collected_at: datetime
