import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    django_api_url: str = Field(..., env="DJANGO_API_URL")

    model_config = SettingsConfigDict(env_file="envs/.local.env", extra="allow")


settings = Settings()

print(os.getenv("DJANGO_API_URL"))
