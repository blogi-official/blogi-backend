from rest_framework import serializers

from apps.models import GeneratedPost


# Clova 요약 결과 미리보기 004
class GeneratedPostPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = [
            "title",
            "content",
            "image_1_url",
            "image_2_url",
            "image_3_url",
            "created_at",
            "copy_count",
        ]


# 사용자 생성 콘텐츠 목록조회 006
class AdminGeneratedPostListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email")

    class Meta:
        model = GeneratedPost
        fields = ["id", "title", "created_at", "user_email"]


# 사용자 생성 콘텐츠 상세조회 007
class AdminGeneratedPostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = [
            "id",
            "title",
            "content",
            "image_1_url",
            "image_2_url",
            "image_3_url",
            "copy_count",
            "created_at",
        ]


# 사용자 생성 콘텐츠 비공개 / 삭제처리 008
class AdminGeneratedPostDeactivateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

    def validate_is_active(self, value):
        if value is not False:
            raise serializers.ValidationError("is_active는 반드시 false여야 합니다.")
        return value
