from django.urls import path

from apps.users.views.auth_views import (
    KakaoCallbackView,
    KakaoLoginDocView,
    KakaoLoginStartView,
    NaverCallbackView,
    NaverLoginDocView,
    NaverLoginStartView,
)
from apps.users.views.keyword_views import KeywordClickLogView, KeywordListAPIView
from apps.users.views.post_views import (
    GeneratedPostDeleteAPIView,
    GeneratedPostPublicDetailAPIView,
    PostCopyAPIView,
    PostPDFDownloadAPIView,
    UserGeneratedPostDetailAPIView,
    UserGeneratedPostListAPIView,
    UserGeneratedPostPatchAPIView,
)
from apps.users.views.profile_views import (
    UserDeleteView,
    UserInterestView,
    UserProfileAPIView,
    UserUpdateView,
)

app_name = "users"

urlpatterns = [
    # 소셜 로그인 콜백
    path("auth/kakao/login/", KakaoLoginStartView.as_view(), name="kakao-login"),
    path("auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
    path("auth/naver/login/", NaverLoginStartView.as_view(), name="naver-login"),
    path("auth/naver/callback/", NaverCallbackView.as_view(), name="naver-callback"),
    # 임시 소셜 로그인 링크뷰
    path("auth/kakao/swagger-login/", KakaoLoginDocView.as_view(), name="kakao-login-doc"),
    path("auth/naver/swagger-login/", NaverLoginDocView.as_view(), name="naver-login-doc"),
    # 닉네임 카테고리 설정
    path("user/interests/", UserInterestView.as_view(), name="user-interests"),
    # 프로필 조회
    path("mypage/me/", UserProfileAPIView.as_view(), name="mypage-profile"),
    # 키워드 조회 및 클릭 기록
    path("keywords/", KeywordListAPIView.as_view(), name="keyword-list"),
    path("keywords/<int:id>/click/", KeywordClickLogView.as_view(), name="keyword-click"),
    # 마이페이지 생성 이력
    path("mypage/posts/", UserGeneratedPostListAPIView.as_view(), name="mypage-posts"),
    path(
        "mypage/posts/<int:pk>/",
        UserGeneratedPostDetailAPIView.as_view(),
        name="mypage-post-detail",
    ),
    # 생성글 조회 및 부가 기능
    path(
        "posts/<int:pk>/",
        GeneratedPostPublicDetailAPIView.as_view(),
        name="generated-post-result",
    ),
    path("posts/<int:id>/copy/", PostCopyAPIView.as_view(), name="post-copy"),
    path(
        "posts/<int:id>/pdf/",
        PostPDFDownloadAPIView.as_view(),
        name="post-pdf-download",
    ),
    # 콘텐츠 생성 상태 변경
    path(
        "posts/<int:post_id>/status/",
        UserGeneratedPostPatchAPIView.as_view(),
        name="post-status-update",
    ),
    path(
        "user/posts/<int:id>/",
        GeneratedPostDeleteAPIView.as_view(),
        name="user-post-delete",
    ),
    # 닉네임 수정 및 회원탈퇴
    path("user/nickname/", UserUpdateView.as_view(), name="user-update"),
    path("user/", UserDeleteView.as_view(), name="user-delete"),
]
