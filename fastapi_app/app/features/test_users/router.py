from app.features.test_users.services import fetch_user_from_django
from fastapi import APIRouter

user_router = APIRouter()


@user_router.get("/users/{user_id}")
async def get_user(user_id: int):
    data = await fetch_user_from_django(user_id)
    return data
