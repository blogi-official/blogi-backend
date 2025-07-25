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
    path("user/interests", UserInterestView.as_view(), name="user-interests"),
    # 프로필 조회
    path("mypage/me", UserProfileAPIView.as_view()),
    # 키워드 조회
    path("keywords", KeywordListAPIView.as_view(), name="keyword-list"),
    # 키워드 클릭 기록 동록
    path("keywords/<int:id>/click", KeywordClickLogView.as_view(), name="keyword-click"),
    # 마이 페이지 생성 이력 조회
    path("mypage/posts", UserGeneratedPostListAPIView.as_view(), name="mypage-posts"),
    path("mypage/posts/<int:pk>", UserGeneratedPostDetailAPIView.as_view(), name="mypage-post-detail"),
    # Mypage 생성 이력 상세조회 / 복사기능 / PDF 다운로드 / 삭제 / 닉네임 관심사 수정 / 회원탈퇴
    path("posts/<int:pk>", GeneratedPostPublicDetailAPIView.as_view(), name="generated-post-result"),
    path("posts/<int:id>/copy", PostCopyAPIView.as_view(), name="post-copy"),
    path("posts/<int:id>/pdf", PostPDFDownloadAPIView.as_view()),
    path("user/posts/<int:id>", GeneratedPostDeleteAPIView.as_view()),
    path("user/nickname", UserUpdateView.as_view(), name="user-update"),
    path("user", UserDeleteView.as_view(), name="user-delete"),
]
