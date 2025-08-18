from rest_framework import serializers

from apps.models import GeneratedPost, Keyword


class KeywordListSerializer(serializers.ModelSerializer):
    is_generated = serializers.SerializerMethodField()

    class Meta:
        model = Keyword
        fields = [
            "id",
            "title",
            "category",
            "is_active",
            "collected_at",
            "is_generated",
        ]

    def get_is_generated(self, obj):
        user = self.context.get("user")
        if not user or not user.is_authenticated:
            return False
        # 로그인한 유저가 해당 키워드로 생성 완료한 게시글 있는지 체크
        return GeneratedPost.objects.filter(user=user, keyword=obj, is_generated=True).exists()
