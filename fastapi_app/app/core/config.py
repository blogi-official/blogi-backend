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

    # 키워드 비활성화처리
    django_api_endpoint_keyword_deactivate: str = Field(
        default="/api/internal/keywords/{id}/deactivate/",
        description="키워드 비활성화 처리 API",
    )

    # Clova 콘텐츠 생성 처리 관련 Endpoints
    django_api_endpoint_article_detail: str = Field(
        default="/api/internal/posts/article-with-images/",
        description="기사+이미지 통합 조회 (keyword_id 기반)",
    )

    django_api_endpoint_generated_post: str = Field(
        default="/api/internal/posts/",
        description="Clova 생성 결과 저장",
    )

    django_api_endpoint_clova_log_success: str = Field(
        default="/api/internal/clova-log/success/",
        description="Clova 생성 성공 로그 저장",
    )

    django_api_endpoint_clova_log_fail: str = Field(
        default="/api/internal/clova-log/fail/",
        description="Clova 생성 실패 로그 저장",
    )

    django_api_endpoint_generated_post_preview: str = Field(
        default="/api/internal/generated-posts/preview",
        description="Clova 생성 결과 미리보기 (기존 결과 반환)",
    )

    # 사용자 로그인용 JWT 토큰 검증용 시크릿
    django_secret_key: str = Field(..., description="JWT 서명용 시크릿 키 (Django와 동일)")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")

    # 내부 서비스 간 통신용 시크릿 키
    internal_secret_key: Optional[str] = Field(None, description="내부 시크릿 키")

    # NAVER
    naver_client_id: str = Field(..., description="네이버 클라이언트 아이디")
    naver_client_secret: str = Field(..., description="네이버 클라이언트 시크릿 키")

    # TODO: Clova Studio 연동 시 아래 항목들 활성화 및 .env 설정 필요
    """
    clova_api_url: str = Field(..., env="CLOVA_API_URL")
    clova_api_key: str = Field(..., env="CLOVA_API_KEY")
    clova_api_secret: str = Field(default="", env="CLOVA_API_SECRET")  # optional
    clova_deployment_name: str = Field(..., env="CLOVA_DEPLOYMENT_NAME")
    clova_system_prompt: str = Field(default="", env="CLOVA_SYSTEM_PROMPT")
    """

    timezone: str = Field(default="Asia/Seoul", description="애플리케이션 기본 타임존")

    model_config = SettingsConfigDict(
        env_file="envs/.local.env",
        extra="allow",
    )


settings = Settings()  # type: ignore
