from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ScrapedArticle(BaseModel):
    keyword_id: int
    title: str
    origin_link: HttpUrl
    content: str
