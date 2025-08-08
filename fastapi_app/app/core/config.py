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

    # Clova 연동
    # Clova Studio API 키 (모든 API 호출에 사용됨)
    clova_api_key: str = Field(..., description="CLOVA Studio API 키")

    # Clova Studio의 OpenAI 호환 API Base URL
    openai_base_url: str = Field(..., description="OpenAI 호환 API base URL (e.g. /v1/openai)")

    # Clova Studio REST API Base URL (튜닝 등)
    clova_base_url: str = Field(..., description="Clova Studio REST API base URL (튜닝용)")

    # Object Storage 버킷 이름
    clova_bucket_name: str = Field(..., description="Clova 튜닝 데이터용 Object Storage 버킷 이름")

    # 튜닝용 학습 데이터 경로 (예: tuning/2025-08/blogi_train.csv)
    clova_data_path: str = Field(..., description="Object Storage 내 학습 데이터 경로")

    # Object Storage 접근을 위한 Access Key
    clova_storage_access_key: str = Field(..., description="Object Storage 접근용 Access Key")

    # Object Storage 접근을 위한 Secret Key
    clova_storage_secret_key: str = Field(..., description="Object Storage 접근용 Secret Key")

    # Clova 튜닝 Task ID (모델 ID)
    clova_tuned_model_id: str = Field(..., description="CLOVA 튜닝 Task ID (v3/tasks/<ID>)")

    # Clova System Prompt (튜닝 모델 프롬프트)
    clova_system_prompt: str = Field(..., description="Clova Studio system prompt (튜닝된 모델 역할)")

    # FastAPI 프록시 주소 (이미지 프록시용)
    fastapi_origin: str = Field(
        ...,
        description="이미지 프록시 요청을 위한 FastAPI 서버 주소 (도메인 또는 포트 포함)",
    )

    timezone: str = Field(default="Asia/Seoul", description="애플리케이션 기본 타임존")

    model_config = SettingsConfigDict(
        env_file="envs/.local.env",
        extra="allow",
    )


settings = Settings()  # type: ignore
