import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

import sentry_sdk
from dotenv import load_dotenv

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ────────────────────────────────────────────────
# .local.env 로딩 (로컬 개발 시만 스위치 켜기)
# ────────────────────────────────────────────────
# 기본값: false → docker나 배포 환경에서는 자동으로 로딩 안 함
# 로컬에서만 .local.env 사용하려면:
#   USE_DOTENV=true python manage.py runserver
if os.getenv("USE_DOTENV", "false").lower() == "true":
    load_dotenv(dotenv_path=BASE_DIR / "envs/.local.env")

# ────────────────────────────────────────────────
# 기본 설정
# ────────────────────────────────────────────────
SECRET_KEY: Optional[str] = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable not set")

# DEBUG 모드
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "debug_toolbar",
    "rest_framework_simplejwt",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
]

CUSTOM_APPS = ["apps"]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
if not REDIS_HOST or not REDIS_PORT:
    raise ValueError("REDIS_HOST and REDIS_PORT must be set")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "ko-KR"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ───────── CORS / CSRF (빈값 필터링 + 로컬 기본 오리진) ─────────
def _csv_env(name: str):
    raw = os.getenv(name, "")
    # 콤마로 나눈 뒤 공백/빈값 제거
    return [x.strip() for x in raw.split(",") if x.strip()]


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# 환경변수에서 가져온 값(스킴 포함) + 로컬 기본값
CORS_ALLOWED_ORIGINS = _csv_env("CORS_ALLOWED_ORIGINS") + [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_TRUSTED_ORIGINS = _csv_env("CSRF_TRUSTED_ORIGINS") + [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


# DRF
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "블로기 Backend API",
    "DESCRIPTION": "블로기 웹 사이트 개발을 위한 API입니다.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
    },
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SECURITY": [
        {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    ],
}

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
if not SENTRY_DSN:
    raise ValueError("SENTRY_DSN must be set. For Error Logging")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 1)),
    profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", 1)),
)

# Static files
STATIC_URL = "static/"

# Social login
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_SECRET = os.getenv("NAVER_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

# Internal API secret
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET")
if not INTERNAL_SECRET:
    raise ValueError("INTERNAL_SECRET must be set for FastAPI internal authentication")

# User model
AUTH_USER_MODEL = "apps.User"

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
