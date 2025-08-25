import logging

from django.utils import timezone
from rest_framework import serializers

from apps.models import GeneratedPost

logger = logging.getLogger(__name__)


# 기사+이미지 조회 005
class ArticleWithImagesSerializer(serializers.Serializer):
    keyword_title = serializers.CharField(source="title")
    content = serializers.CharField()
    image_urls = serializers.ListField(child=serializers.URLField(), max_length=3)


# 생성 컨텐츠 저장 007
class InternalGeneratedPostCreateSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    image_1_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    image_2_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    image_3_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)


# 성공/실패 로그 006
class ClovaSuccessLogSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    response_time_ms = serializers.IntegerField(required=False)


class ClovaFailLogSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    error_message = serializers.CharField()
    response_time_ms = serializers.IntegerField(required=False)


class InternalGeneratedPostDetailSerializer(serializers.ModelSerializer):
    """clova로 생성된 콘텐츠 조회"""

    keyword_id = serializers.IntegerField(source="keyword.id")
    user_id = serializers.IntegerField(source="user.id")

    class Meta:
        model = GeneratedPost
        fields = [
            "id",
            "title",
            "content",
            "image_1_url",
            "image_2_url",
            "image_3_url",
            "keyword_id",
            "user_id",
        ]


class InternalGeneratedPostUpdateSerializer(serializers.ModelSerializer):
    """clova로 생성된 콘텐츠 수정(재생성)"""

    class Meta:
        model = GeneratedPost
        fields = [
            "title",
            "content",
            "image_1_url",
            "image_2_url",
            "image_3_url",
            "created_at",
        ]

    def update(self, instance, validated_data):
        instance.is_generated = True
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.created_at = timezone.now()
        instance.save()
        return instance
