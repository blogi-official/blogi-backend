from rest_framework import serializers

from apps.models import Keyword


# 공개/비공개 토글 001
class KeywordToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["id", "title", "is_active"]


# 키워드 콘텐츠 상세조회 002


class KeywordDetailSerializer(serializers.Serializer):
    #  제목은 키워드의 제목을 사용
    title = serializers.CharField(source="keyword.title")
    # 기사 본문/원문 링크는 Article에서
    content = serializers.CharField(source="article.content")
    original_url = serializers.CharField(source="article.origin_link")
    # 생성글 이미지 3개 (없을 수 있으므로 allow_null)
    image_1_url = serializers.CharField(source="generated_post.image_1_url", allow_null=True)
    image_2_url = serializers.CharField(source="generated_post.image_2_url", allow_null=True)
    image_3_url = serializers.CharField(source="generated_post.image_3_url", allow_null=True)


# 키워드 제목 수정 003


class KeywordTitleUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        required=True,
        max_length=255,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "blank": "제목 필드는 필수이며 빈 문자열일 수 없습니다.",
            "max_length": "제목은 255자를 초과할 수 없습니다.",
        },
    )

    class Meta:
        model = Keyword
        fields = ["title"]
