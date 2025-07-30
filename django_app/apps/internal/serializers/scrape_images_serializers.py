from rest_framework import serializers

from apps.models import Keyword


class KeywordImageTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["id", "title"]


class ImageSaveRequestSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    images = serializers.ListField(child=serializers.URLField(), max_length=3, allow_empty=False)
