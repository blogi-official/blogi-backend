# apps/internal/urls.py

"""
내부 연동용 API
- FastAPI와 Django 간 콘텐츠 동기화용 엔드포인트 모음
- 외부 공개용이 아닌 내부 시스템 간 호출 전용
"""
from django.urls import path

from apps.internal.views.fetch_aritcle_views import (
    ArticleCreateAPIView,
    KeywordListAPIView,
)
from apps.internal.views.generate_post_views import (
    ClovaFailLogCreateAPIView,
    ClovaSuccessLogCreateAPIView,
    GeneratedPostPreviewAPIView,
    InternalArticleDetailAPIView,
    InternalGeneratedPostCreateAPIView,
    InternalRegeneratedPostAPIView,
)
from apps.internal.views.keyword import KeywordDeactivateAPIView
from apps.internal.views.scrap_titles_views import KeywordCreateAPIView
from apps.internal.views.scrape_images_views import (
    ImageSaveAPIView,
    KeywordMarkCollectedAPIView,
    KeywordNextImageTargetAPIView,
)

app_name = "internal"

urlpatterns = [
    path(
        "keywords/next-image-target/",
        KeywordNextImageTargetAPIView.as_view(),
        name="internal-keywords-next-image-target",
    ),
    path("images/", ImageSaveAPIView.as_view(), name="internal-images-save"),
    path(
        "keywords/<int:id>/collected/",
        KeywordMarkCollectedAPIView.as_view(),
        name="internal-keywords-mark-collected",
    ),
    path(
        "keywords/<int:id>/deactivate/",
        KeywordDeactivateAPIView.as_view(),
        name="keyword-deactivate",
    ),
    # 키워드 생성: FastAPI가 네이버 등에서 수집한 키워드를 Django에 저장할 때 사용 (POST)
    path("posts/", KeywordCreateAPIView.as_view(), name="keyword-create"),
    # 키워드 목록 조회: FastAPI가 본문 수집 대상 키워드를 조회할 때 사용 (GET)
    path("keywords/", KeywordListAPIView.as_view(), name="keyword-list"),
    # 기사 본문 생성: FastAPI가 수집한 기사 본문 데이터를 Django에 저장할 때 사용 (POST)
    path("article/create/", ArticleCreateAPIView.as_view(), name="article-create"),
    # 기사 본문 , 이미지 조회 (GET) 005
    path(
        "articles/<int:keyword_id>/",
        InternalArticleDetailAPIView.as_view(),
        name="internal-article-detail",
    ),
    # Clova 생성 결과 저장 (POST) 007
    path(
        "generated-posts/",
        InternalGeneratedPostCreateAPIView.as_view(),
        name="internal-post-create",
    ),
    # Clova 생성 결과 조회 및 재생성 저장(GET, PATCH)
    path(
        "posts/<int:post_id>/",
        InternalRegeneratedPostAPIView.as_view(),
        name="internal_post_detail_update",
    ),
    # Clova 생성 성공/실패 로그 생성 (POST) 006
    path(
        "clova-log/success/",
        ClovaSuccessLogCreateAPIView.as_view(),
        name="internal-clova-log-success",
    ),
    path(
        "clova-log/fail/",
        ClovaFailLogCreateAPIView.as_view(),
        name="internal-clova-log-fail",
    ),
    # Clova 생성 중복 프리뷰 반환
    path(
        "generated-posts/preview/",
        GeneratedPostPreviewAPIView.as_view(),
        name="generated-post-preview",
    ),
]
