from app.core.config import settings

CATEGORY_MAP = {
    "연예": "엔터 종합",
    "경제": "경제 종합",
    "스포츠": "스포츠 종합",
    "패션": "패션뷰티 종합",
    "자동차": "카테크 종합",
    "여행": "여행맛집 종합",
    "맛집": "맛집/카페",
}

DJANGO_API_ENDPOINT = f"http://{settings.django_api_url}/api/internal/posts/"
