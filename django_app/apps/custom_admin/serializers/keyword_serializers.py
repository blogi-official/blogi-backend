from typing import Any

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


# 관리자용 키워드 목록조회 API(신설)


class KeywordListItemSerializer(serializers.ModelSerializer):
    generated_count = serializers.IntegerField(read_only=True)
    image_count = serializers.IntegerField(read_only=True)
    last_generated_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.SerializerMethodField()  # 모델에 없어도 안전

    class Meta:
        model = Keyword
        fields = [
            "id",
            "title",
            "category",
            "source_category",
            "is_active",
            "is_collected",
            "collected_at",
            "created_at",
            "updated_at",
            "generated_count",
            "image_count",
            "last_generated_at",
        ]

    def get_updated_at(self, obj):
        # Keyword에는 updated가 없으니 collected_at -> created_at 순으로 폴백
        for cand in ("updated_at", "modified_at", "last_modified", "changed_at", "collected_at"):
            if hasattr(obj, cand):
                return getattr(obj, cand)
        return getattr(obj, "created_at", None)


# 커스텀 페이지네이션 스키마 (pagination + data)
class PaginationMetaSerializer(serializers.Serializer):
    current_page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()
    page_size = serializers.IntegerField()
    max_page_size = serializers.IntegerField()


class AdminKeywordListPageSerializer(serializers.Serializer):
    pagination = PaginationMetaSerializer()
    data: Any = KeywordListItemSerializer(many=True)
