from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from app.features.internal.fetch_article.services import scrape_and_send_articles
from app.features.internal.fetch_image.service import fetch_and_save_images
from app.features.internal.scrape_titles.services import fetch_and_send_to_django


def register_periodic_tasks(app: FastAPI):
    @app.on_event("startup")
    @repeat_every(seconds=3600)  # 1시간마다 실행
    async def periodic_scrape():
        await fetch_and_send_to_django()

    @app.on_event("startup")
    @repeat_every(seconds=1800)
    async def periodic_scrape_articles():
        await scrape_and_send_articles()

    @app.on_event("startup")
    @repeat_every(seconds=600)  # 10분마다 대표 이미지 수집
    async def periodic_fetch_images():
        await fetch_and_save_images()
