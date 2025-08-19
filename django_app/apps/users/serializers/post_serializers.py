from rest_framework import serializers

from apps.models import CopyLog, GeneratedPost


# 마이페이지 생성 콘텐츠 목록 조회(014)
class GeneratedPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = ["id", "title", "created_at", "copy_count"]


# 마이페이지 생성 콘텐츠 상세 조회(015) / 생성결과보기 (003)
class GeneratedPostDetailSerializer(serializers.ModelSerializer):
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


# 복사 기능 (004)
class CopyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyLog
        fields = ["id", "user", "post", "copied_at"]
        read_only_fields = fields


# 콘텐츠 생성 상태 변경
class GeneratedPostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = ["id", "is_generated"]
        read_only_fields = ["id"]
