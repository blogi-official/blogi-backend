import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.common.scheduler import register_periodic_tasks

load_dotenv("/app/envs/.prod.env")

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
