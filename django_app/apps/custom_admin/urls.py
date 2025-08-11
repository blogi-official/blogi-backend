from django.urls import path

from apps.custom_admin.views.dashboard_views import (
    ClovaStatsAPIView,
    DailyStatsAPIView,
    TopKeywordAPIView,
)
from apps.custom_admin.views.keyword_views import (
    KeywordDetailAPIView,
    KeywordTitleUpdateAPIView,
    KeywordToggleView, KeywordListAPIView,
)
from apps.custom_admin.views.post_views import (
    ClovaPreviewAPIView,
    ClovaRegenerateAPIView,
    GeneratedPostDeactivateOrDeleteAPIView,
    GeneratedPostDetailAPIView,
    GeneratedPostListAPIView,
)
from apps.custom_admin.views.user_views import (
    AdminLoginAPIView,
    AdminUserGeneratedPostListAPIView,
    AdminUserListAPIView,
)

app_name = "custom_admin"

urlpatterns = [
    # 키워드 관리
    path(
        "titles/<int:id>/toggle/",
        KeywordToggleView.as_view(),
        name="admin-keyword-toggle",
    ),
    path("titles/<int:id>/", KeywordDetailAPIView.as_view(), name="admin-keyword-detail"),
    path(
        "titles/<int:id>/title/",
        KeywordTitleUpdateAPIView.as_view(),
        name="admin-keyword-title-update",
    ),
    path(
        "titles/<int:id>/preview/",
        ClovaPreviewAPIView.as_view(),
        name="admin-clova-preview",
    ),
    path(
        "titles/<int:id>/regenerate/",
        ClovaRegenerateAPIView.as_view(),
        name="admin-clova-regenerate",
    ),
    # 생성 콘텐츠 관리
    path("generated/", GeneratedPostListAPIView.as_view(), name="admin-generated-posts"),
    path(
        "generated/<int:id>/",
        GeneratedPostDetailAPIView.as_view(),
        name="admin-generated-post-detail",
    ),
    path(
        "generated/<int:id>/manage/",
        GeneratedPostDeactivateOrDeleteAPIView.as_view(),
        name="admin-generated-post-manage",
    ),
    # 유저 관리
    path("auth/admin-login/", AdminLoginAPIView.as_view(), name="admin-login"),
    path("users/", AdminUserListAPIView.as_view(), name="admin-user-list"),
    path(
        "users/<int:user_id>/generated/",
        AdminUserGeneratedPostListAPIView.as_view(),
        name="admin-user-generated-posts",
    ),
    # 대시보드
    path("dashboard/daily-stats/", DailyStatsAPIView.as_view(), name="daily-stats"),
    path(
        "dashboard/top-keywords/",
        TopKeywordAPIView.as_view(),
        name="admin_dashboard_top_keywords",
    ),
    path(
        "dashboard/clova-stats/",
        ClovaStatsAPIView.as_view(),
        name="admin-dashboard-clova-stats",
    ),
    path("titles/", KeywordListAPIView.as_view(), name="admin_titles_list"),
]
