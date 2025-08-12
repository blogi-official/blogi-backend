import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import api_router
from app.common.scheduler import register_periodic_tasks
from app.core.config import settings

IS_LOCAL = os.getenv("APP_ENV", "local") == "local"

root_path = "" if IS_LOCAL else "/fastapi"
openapi_url = f"{root_path}/openapi.json" if root_path else "/openapi.json"

app = FastAPI(
    root_path=root_path,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=openapi_url,
    title="Blogi FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["health"])
def read_root():
    return {"message": "Hello FastAPI"}


@app.get("/ping", tags=["health"])
def ping():
    return {"pong": True}
