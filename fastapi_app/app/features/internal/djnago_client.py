from app.common.http_client import post_json, get_json
from app.core.config import settings

async def fetch_keywords_from_django():
    headers = {"X-Internal-Secret": settings.internal_secret_key}
    return await get_json(settings.django_api_endpoint_keywords_get, headers=headers)

async def send_keywords_to_django(data_list):
    headers = {"X-Internal-Secret": settings.internal_secret_key}
    return await post_json(settings.django_api_endpoint_keywords_post, data_list, headers)

async def send_articles_to_django(data_list):
    headers = {"X-Internal-Secret": settings.internal_secret_key}
    return await post_json(settings.django_api_endpoint_articles_post, data_list, headers)