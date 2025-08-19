from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GenerateClovaPostRequest(BaseModel):
    keyword_id: int = Field(..., description="Clova 콘텐츠를 생성할 대상 키워드 ID")
    user_id: int = Field(..., description="생성 요청한 사용자 ID")


class GenerateClovaPostResponse(BaseModel):
    post_id: Optional[int] = Field(None, description="생성된 게시물 ID (성공 시)")
    created_at: Optional[datetime] = Field(None, description="게시물 생성 시간 (성공 시)")
    status: str = Field(..., description="처리 결과 상태: success 또는 failed")
    error_message: Optional[str] = Field(None, description="오류 발생 시 메시지 (optional)")
    from_cache: Optional[bool] = Field(
        False,
        description="이미 생성된 콘텐츠 여부 (True: 기존 글 재사용, False: 새로 생성됨)",
    )


class RegenerateClovaPostRequest(BaseModel):
    """Clova 콘텐츠 재생성 요청 스키마"""

    user_id: int = Field(..., description="재생성을 요청한 사용자 ID")
