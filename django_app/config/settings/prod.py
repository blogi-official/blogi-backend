# config/settings/prod.py
import os

from .base import *

DEBUG = False


def _split_env(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


# ── ALLOWED_HOSTS ───────────────────────────────────────────
_base_allowed = _split_env("DJANGO_ALLOWED_HOSTS", "")
_internal_hosts = ["localhost", "127.0.0.1", "django", "nginx", "fastapi"]
ALLOWED_HOSTS = list(dict.fromkeys(_base_allowed + _internal_hosts))
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [
        "backend.blogi.store",
        "localhost",
        "127.0.0.1",
        "django",
        "nginx",
        "fastapi",
    ]

# ── CORS / CSRF ─────────────────────────────────────────────
# 브라우저 오리진만 CORS에 넣습니다.
CORS_ALLOWED_ORIGINS = _split_env("CORS_ALLOWED_ORIGINS", "")
if CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = False  # base.py의 allow_all 무효화

# CSRF는 스킴 필수. env 그대로 사용(프론트 오리진 중심).
CSRF_TRUSTED_ORIGINS = _split_env("CSRF_TRUSTED_ORIGINS", "")

# ── 정적/미디어 ─────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── 가시화 로그 ─────────────────────────────────────────────
print("=== DJANGO PROD SETTINGS LOADED ===")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
print(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
