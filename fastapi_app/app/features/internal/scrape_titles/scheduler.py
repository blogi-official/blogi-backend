from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from app.features.internal.scrape_titles.services import fetch_and_send_to_django


def register_periodic_tasks(app: FastAPI):
    @app.on_event("startup")
    @repeat_every(seconds=3600)  # 1시간마다 실행
    async def periodic_scrape():
        await fetch_and_send_to_django()
