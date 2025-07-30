from typing import List

from pydantic import BaseModel


# 응답으로 반환될 JSON 형태
class ImageFetchResponse(BaseModel):
    images: List[str]
