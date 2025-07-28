# apps/custom_admin/serializers/user_serializers.py
from rest_framework import serializers

from apps.models import GeneratedPost, User


# 관리자 로그인
class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# 가입 유저 목록조회 009
class AdminUserListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="id")

    class Meta:
        model = User
        fields = ["user_id", "email", "provider", "created_at"]


# 유저별 콘텐츠 생성 이력조회 010
class AdminUserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class AdminUserGeneratedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = ["id", "title", "created_at", "copy_count"]
