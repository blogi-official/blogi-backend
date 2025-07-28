from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    django_api_url: str = Field(
        default="http://localhost:8000", description="Django API base URL"
    )

    # 사용자 로그인용 JWT 토큰 검증용 시크릿
    django_secret_key: str = Field(
        ..., description="JWT 서명용 시크릿 키 (Django와 동일)"
    )
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")

    # 내부 서비스 간 통신용 시크릿 키
    internal_secret_key: Optional[str] = Field(None, description="JWT 시크릿 키")

    timezone: str = Field(default="Asia/Seoul", description="애플리케이션 기본 타임존")

    model_config = SettingsConfigDict(
        env_file="envs/.local.env",
        extra="allow",
    )


settings = Settings()  # type: ignore
