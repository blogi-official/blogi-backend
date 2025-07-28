from fastapi import APIRouter

from app.features.internal.router import internal_router
from app.features.test_users.router import user_router

api_router = APIRouter(prefix="/api/v1")

# 각 개별 라우터들을 api_router에 포함
api_router.include_router(user_router)
api_router.include_router(internal_router)
