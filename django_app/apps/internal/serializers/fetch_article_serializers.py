import logging

from rest_framework import serializers

from apps.models import Article
from apps.models import Keyword

logger = logging.getLogger(__name__)

# 키워드 조회(GET)
class KeywordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["id", "title"]


# 기사 본문 생성(POST)
class ScrapedArticleCreateSerializer(serializers.ModelSerializer):
    keyword_id = serializers.PrimaryKeyRelatedField(queryset=Keyword.objects.all())

    class Meta:
        model = Article
        fields = ["keyword_id", "title", "content", "origin_link"]

    def create(self, validated_data):
        keyword = validated_data.pop('keyword_id')

        # 여기에서 중복 체크 & 저장
        if Article.objects.filter(keyword=keyword).exists():
            logger.info(f"이미 수집된 키워드입니다. 저장 스킵: {keyword.id}")
            return None  # 또는 raise ValidationError 등
        else:
            article = Article.objects.create(keyword=keyword, **validated_data)
            keyword.is_collected = True
            keyword.save()
            return article
        #return Article.objects.create(keyword=keyword, **validated_data)
