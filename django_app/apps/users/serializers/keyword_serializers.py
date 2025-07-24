from rest_framework import serializers

from apps.models import Keyword


class KeywordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = [
            "id",
            "title",
            "category",
            "is_active",
            "collected_at",
        ]
