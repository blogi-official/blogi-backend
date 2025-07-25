from pydantic import BaseModel
from datetime import datetime

class ScrapedKeyword(BaseModel):
    title: str
    category: str
    source: str = "네이버"
    collected_at: datetime

class ScrapeResponse(BaseModel):
    message: str
    created_count: int
    skipped_count: int