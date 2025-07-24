import os

from .base import *

DEBUG = False

# TODO 운영용 도메인 허용 (기본값 비워두고 나중에 .env에서 주입) #.env에서 prod 추가필요
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(" ")

# 정적 파일 및 미디어 설정
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# CORS/CSRF 설정
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(" ")  # TODO 배포전 추가

if ALLOWED_ORIGINS and ALLOWED_ORIGINS != [""]:
    CORS_ALLOWED_ORIGINS += ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS += ALLOWED_ORIGINS
