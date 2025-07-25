# apps/users/views/auth.py

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.views import View
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth_serializers import (
    KakaoLoginSerializer,
    NaverLoginSerializer,
)


class KakaoCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"detail": "인가 코드가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = KakaoLoginSerializer(data={"code": code})

        serializer.is_valid(raise_exception=True)
        token_response = serializer.save()

        return Response(token_response, status=status.HTTP_200_OK)


class NaverCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return Response(
                {"detail": "code 또는 state가 누락되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = NaverLoginSerializer(data={"code": code, "state": state})
        serializer.is_valid(raise_exception=True)
        token_response = serializer.save()

        return Response(token_response, status=status.HTTP_200_OK)


class KakaoLoginStartView(View):
    def get(self, request):
        kakao_auth_url = (
            "https://kauth.kakao.com/oauth/authorize?"
            f"client_id={settings.KAKAO_CLIENT_ID}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
        )
        return redirect(kakao_auth_url)


class NaverLoginStartView(View):
    def get(self, request):
        state = get_random_string(12)
        naver_auth_url = (
            "https://nid.naver.com/oauth2.0/authorize?"
            f"response_type=code"
            f"&client_id={settings.NAVER_CLIENT_ID}"
            f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
            f"&state={state}"
        )
        return redirect(naver_auth_url)


# 임시 로그인 구현 view
class KakaoLoginDocView(APIView):
    @extend_schema(
        tags=["[Auth] 소셜 로그인"],
        summary="카카오 로그인 시작 (Swagger용)",
        description="""
📌 **카카오 로그인 안내**

👉 [카카오 로그인 바로가기](http://127.0.0.1:8000/api/auth/kakao/login/)

해당 링크를 클릭하면 카카오 로그인 페이지로 리디렉션됩니다.  
이 API는 Swagger 문서에 노출시키기 위한 설명용입니다.
        """,
        responses={200: None},
    )
    def get(self, request):
        return Response({"message": "카카오 로그인은 위 링크를 클릭하세요"})


class NaverLoginDocView(APIView):
    @extend_schema(
        tags=["[Auth] 소셜 로그인"],
        summary="네이버 로그인 시작 (Swagger용)",
        description="""
📌 **네이버 로그인 안내**

👉 [네이버 로그인 바로가기](http://127.0.0.1:8000/api/auth/naver/login/)

해당 링크를 클릭하면 네이버 로그인 페이지로 리디렉션됩니다.  
이 API는 Swagger 문서에 노출시키기 위한 설명용입니다.
        """,
        responses={200: None},
    )
    def get(self, request):
        return Response({"message": "네이버 로그인은 위 링크를 클릭하세요"})
