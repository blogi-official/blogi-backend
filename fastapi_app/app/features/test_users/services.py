import httpx

from app.core.config import settings

# async def fetch_user_from_django(user_id: int):
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"{settings.django_api_url}/api/v1/users/{user_id}/",
#             follow_redirects=True
#         )
#         response.raise_for_status()
#         return response.json()


async def fetch_user_from_django(user_id: int):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url=f"{settings.django_api_url}/api/v1/users/{user_id}/"
        )
        response.raise_for_status()
        return response.json()
