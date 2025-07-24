from app.api.v1.routers import api_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
