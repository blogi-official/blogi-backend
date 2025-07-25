from django.urls import path

from apps.custom_admin.views.keyword_views import (
    KeywordDetailAPIView,
    KeywordTitleUpdateAPIView,
    KeywordToggleView,
)
from apps.custom_admin.views.post_views import (
    ClovaPreviewAPIView,
    ClovaRegenerateAPIView,
)

app_name = "custom_admin"

urlpatterns = [
    # 키워드 관리
    path("titles/<int:id>/toggle", KeywordToggleView.as_view(), name="admin-keyword-toggle"),
    path("titles/<int:id>", KeywordDetailAPIView.as_view(), name="admin-keyword-detail"),
    path("titles/<int:id>/title", KeywordTitleUpdateAPIView.as_view(), name="admin-keyword-title-update"),
    path("titles/<int:id>/preview", ClovaPreviewAPIView.as_view(), name="admin-clova-preview"),
    path("titles/<int:id>/regenerate", ClovaRegenerateAPIView.as_view(), name="admin-clova-regenerate"),
]
