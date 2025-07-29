from django.db.models import Q
from rest_framework import serializers

from apps.models import Keyword


class ScrapedKeywordBulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        total_count = len(validated_data)

        # (title, category) 쌍 추출
        key_tuples = {(item["title"], item["category"]) for item in validated_data}

        # 기존 키워드 조회
        existing_qs = Keyword.objects.filter(
            Q(**{"title__in": [t for t, _ in key_tuples]}) & Q(**{"category__in": [c for _, c in key_tuples]})
        )
        # 정확한 중복 판별 위해 dict 매핑
        existing_map = {(k.title, k.category): k for k in existing_qs}

        to_create = []
        to_update = []

        for item in validated_data:
            key = (item["title"], item["category"])
            if key in existing_map:
                obj = existing_map[key]

                # 실제로 값이 달라졌을 때만 업데이트
                has_changed = (
                    obj.collected_at != item["collected_at"]
                    or obj.source_category != item["source_category"]
                    or obj.is_collected != item.get("is_collected", False)
                )

                if has_changed:
                    obj.collected_at = item["collected_at"]
                    obj.source_category = item["source_category"]
                    obj.is_collected = item.get("is_collected", False)
                    to_update.append(obj)
            else:
                # 신규 생성 대상
                to_create.append(
                    Keyword(
                        title=item["title"],
                        category=item["category"],
                        source_category=item["source_category"],
                        collected_at=item["collected_at"],
                        is_collected=item.get("is_collected", False),
                    )
                )

        # 실제 저장 처리
        if to_create:
            Keyword.objects.bulk_create(to_create)
        if to_update:
            Keyword.objects.bulk_update(to_update, ["collected_at", "source_category", "is_collected"])

        return {
            "created": to_create,
            "updated": to_update,
            "created_count": len(to_create),
            "updated_count": len(to_update),
            "total_count": total_count,
        }


class ScrapedKeywordBulkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["title", "category", "source_category", "collected_at", "is_collected"]
        list_serializer_class = ScrapedKeywordBulkListSerializer
        validators = []  # unique validation 비활성화

    def validate(self, attrs):
        return attrs
