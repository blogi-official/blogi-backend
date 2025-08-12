import os

from .base import *

DEBUG = False

# ── Hosts ─────────────────────────────────────────────
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

# ── Static/Media: docker volume 경로와 일치 ──────────
STATIC_URL = "static/"
STATIC_ROOT = "/blogi/app/static"

MEDIA_URL = "media/"
MEDIA_ROOT = "/blogi/app/media"

# ── CORS/CSRF ────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False  # base의 True를 덮어쓰기 (매우 중요)

ALLOWED_ORIGINS = [o for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o]
TRUSTED = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o]

if ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
if TRUSTED:
    CSRF_TRUSTED_ORIGINS = TRUSTED  # https:// 포함 필수

# ── HTTPS 보안 ───────────────────────────────────────
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── debug-toolbar 비활성 (base가 항상 추가하는 경우) ─────
if "debug_toolbar" in INSTALLED_APPS:
    INSTALLED_APPS.remove("debug_toolbar")
if "debug_toolbar.middleware.DebugToolbarMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")

# (선택) prod에서 DRF renderer 최소화로 성능/보안 강화
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
