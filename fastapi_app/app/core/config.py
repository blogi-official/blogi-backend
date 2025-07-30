from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # django_api
    django_api_url: str = Field(default="http://localhost:8000", description="Django API base URL")
    django_api_endpoint_keywords_get: str = Field(..., description="Django GET API 키워드 목록 조회(GET) URL")
    django_api_endpoint_keywords_post: str = Field(..., description="Django API 키워드 저장(POST) 저장 URL")
    django_api_endpoint_articles_post: str = Field(..., description="Django API 기사 본문 저장(POST) 본문 URL")

    # 사용자 로그인용 JWT 토큰 검증용 시크릿
    django_secret_key: str = Field(..., description="JWT 서명용 시크릿 키 (Django와 동일)")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")

    # 내부 서비스 간 통신용 시크릿 키
    internal_secret_key: Optional[str] = Field(None, description="내부 시크릿 키")

    # NAVER
    naver_client_id: str = Field(..., description="네이버 클라이언트 아이디")
    naver_client_secret: str = Field(..., description="네이버 클라이언트 시크릿 키")

    timezone: str = Field(default="Asia/Seoul", description="애플리케이션 기본 타임존")

    model_config = SettingsConfigDict(
        env_file="envs/.local.env",
        extra="allow",
    )


settings = Settings()  # type: ignore
