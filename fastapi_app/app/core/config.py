from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # django_api
    django_api_url: str = Field(default="http://localhost:8000", description="Django API base URL")
    django_api_endpoint_keywords_get: str = Field(..., description="Django GET API 키워드 목록 조회(GET) URL")
    django_api_endpoint_keywords_post: str = Field(..., description="Django API 키워드 저장(POST) 저장 URL")
    django_api_endpoint_articles_post: str = Field(..., description="Django API 기사 본문 저장(POST) 본문 URL")

    # Kakao 이미지 검색 API 키
    kakao_rest_api_key: str = Field(..., description="카카오 이미지 검색용 REST API Key")

    # 내부 키워드 수집/저장 관련 Endpoint 3개
    django_api_endpoint_keyword_image_target: str = Field(
        default="/api/internal/keywords/next-image-target/",
        description="대표 이미지 수집 대상 키워드 조회",
    )
    django_api_endpoint_save_images: str = Field(
        default="/api/internal/images/",
        description="이미지 저장 API",
    )
    django_api_endpoint_mark_collected: str = Field(
        default="/api/internal/keywords/{id}/collected/",
        description="키워드 수집 완료 처리",
    )

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
