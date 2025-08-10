from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.common.scheduler import register_periodic_tasks

app = FastAPI(
    root_path="/fastapi",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(api_router)

# register_periodic_tasks(app)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
