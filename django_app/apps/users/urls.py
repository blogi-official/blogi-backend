from django.urls import path

from apps.users.views.auth_views import (
    KakaoCallbackView,
    KakaoLoginStartView,
    NaverCallbackView,
    NaverLoginStartView,
)
from apps.users.views.keyword_views import KeywordListAPIView
from apps.users.views.profile_views import UserInterestView, UserProfileAPIView

app_name = "users"

urlpatterns = [
    # 소셜 로그인 콜백
    path("auth/kakao/login/", KakaoLoginStartView.as_view(), name="kakao-login"),
    path("auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
    path("auth/naver/login/", NaverLoginStartView.as_view(), name="naver-login"),
    path("auth/naver/callback/", NaverCallbackView.as_view(), name="naver-callback"),
    # 닉네임 카테고리 설정
    path("user/interests", UserInterestView.as_view(), name="user-interests"),
    # 프로필 조회
    path("mypage/me", UserProfileAPIView.as_view()),
    # 키워드 조회
    path("keywords", KeywordListAPIView.as_view(), name="keyword-list"),
]
