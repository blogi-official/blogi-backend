from fastapi import APIRouter

# 스케줄러 관리 라우터 (항상 등록, 인증은 라우터 내부에서 처리)
from app.api.v1.scheduler_admin import router as scheduler_admin_router
from app.features.internal.router import internal_router
from app.features.test_users.router import user_router

api_router = APIRouter(prefix="/api/v1")

# 각 개별 라우터들을 api_router에 포함
api_router.include_router(user_router)
api_router.include_router(internal_router)
api_router.include_router(scheduler_admin_router)
