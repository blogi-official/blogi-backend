from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.features.internal.scrape_titles.scheduler import \
    register_periodic_tasks

app = FastAPI()
app.include_router(api_router)

register_periodic_tasks(app)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
