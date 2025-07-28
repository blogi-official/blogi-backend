from rest_framework import serializers

from apps.models import Keyword


class ScrapedKeywordBulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        # FastAPI에서 받은 총 데이터 수 (저장 요청한 키워드 개수)
        total_count = len(validated_data)

        keyword_objects = [
            Keyword(
                title=item["title"],
                category=item["category"],
                source_category=item["source_category"],
                collected_at=item["collected_at"],
                is_collected=item.get("is_collected", False),
            )
            for item in validated_data
        ]

        # 중복 시 업데이트, 없으면 새로 생성
        objs = Keyword.objects.bulk_create(
            keyword_objects,
            update_conflicts=True,
            update_fields=["collected_at", "source_category", "is_collected"],
            unique_fields=["title", "category"],
        )

        # 새로 생성된 레코드 수
        created_count = len(objs)
        # 중복되어 새로 생성되지 않은(업데이트된) 레코드 수
        skipped_count = total_count - created_count

        return {
            "created": objs,
            "created_count": created_count,
            "skipped_count": skipped_count,
            "total_count": total_count,
        }


class ScrapedKeywordBulkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["title", "category", "source_category", "collected_at", "is_collected"]
        list_serializer_class = ScrapedKeywordBulkListSerializer
        # unique validation 무효화
        validators = []

    def validate(self, attrs):
        return attrs
