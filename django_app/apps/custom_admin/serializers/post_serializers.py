from rest_framework import serializers

from apps.models import GeneratedPost


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
