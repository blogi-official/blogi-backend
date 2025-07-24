import requests
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.models import User


class KakaoLoginSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get("code")
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise serializers.ValidationError("카카오 토큰 요청 실패")

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise serializers.ValidationError("Access token 없음")

        # 유저 정보 요청
        user_info_response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info_response.status_code != 200:
            raise serializers.ValidationError("카카오 사용자 정보 요청 실패")

        user_info = user_info_response.json()
        kakao_id = user_info.get("id")
        kakao_account = user_info.get("kakao_account", {})

        email = kakao_account.get("email", f"kakao_{kakao_id}@example.com")
        nickname = kakao_account.get("profile", {}).get("nickname", "")
        profile_image = kakao_account.get("profile", {}).get("profile_image_url", "")

        user, _ = User.objects.get_or_create(
            social_id=str(kakao_id),
            provider=User.Provider.KAKAO,
            defaults={
                "email": email,
                "nickname": nickname,
                "profile_image": profile_image,
            },
        )

        # JWT 발급
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "nickname": user.nickname,
            "provider": user.provider,
        }

    def create(self, validated_data):
        return validated_data


class NaverLoginSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()

    def validate(self, data):
        import requests
        from django.conf import settings

        code = data.get("code")
        state = data.get("state")

        # 1. access_token 요청
        token_url = "https://nid.naver.com/oauth2.0/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_SECRET,
            "code": code,
            "state": state,
        }
        token_res = requests.get(token_url, params=params)
        if token_res.status_code != 200:
            raise serializers.ValidationError("NAVER 토큰 요청 실패")

        access_token = token_res.json().get("access_token")
        if not access_token:
            raise serializers.ValidationError("NAVER access_token 누락")

        # 2. 사용자 정보 요청
        user_info_res = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info_res.status_code != 200:
            raise serializers.ValidationError("NAVER 사용자 정보 요청 실패")

        naver_user = user_info_res.json().get("response")
        if not naver_user or "id" not in naver_user:
            raise serializers.ValidationError("NAVER 사용자 정보 누락")

        self.naver_id = naver_user.get("id")
        self.email = naver_user.get("email", "")
        return data

    def save(self, **kwargs):
        user, _ = User.objects.get_or_create(provider="naver", social_id=self.naver_id, defaults={"email": self.email})

        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user_info": {
                "id": user.id,
                "email": user.email,
                "provider": user.provider,
            },
        }
