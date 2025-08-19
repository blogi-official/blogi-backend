# 임시 테스트용 코드
import asyncio

from app.features.internal.fetch_image.kakao_client import fetch_kakao_images


async def test():
    result = await fetch_kakao_images("부산 바다")
    print(result)


asyncio.run(test())
