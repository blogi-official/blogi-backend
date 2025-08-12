import os

from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.common.scheduler import register_periodic_tasks

# nano /etc/environment 혹은 vi /etc/environment 접속
# ENV=production 추가 작성 및 저장 후 종료
# source /etc/environment 혹은 sudo reboot 재부팅(권장)
if os.getenv("ENV") == "production":
    app = FastAPI(
        root_path="/fastapi",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
else:
    app = FastAPI()

app.include_router(api_router)

# register_periodic_tasks(app)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
