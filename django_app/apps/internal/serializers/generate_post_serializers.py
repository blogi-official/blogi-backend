from rest_framework import serializers


# 기사+이미지 조회 005
class ArticleWithImagesSerializer(serializers.Serializer):
    title = serializers.CharField()
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
