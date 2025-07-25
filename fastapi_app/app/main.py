from fastapi import FastAPI

from app.api.v1.routers import api_router

# print("[DEBUG] api_router 포함 라우터 확인:", api_router.routes)


app = FastAPI()
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
