from typing import List

from pydantic import BaseModel, HttpUrl


class ImageFetchResponse(BaseModel):
    images: List[HttpUrl]
