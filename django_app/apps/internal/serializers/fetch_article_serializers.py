import logging

from rest_framework import serializers

from apps.models import Article, Keyword

logger = logging.getLogger(__name__)


# 키워드 조회(GET)
class KeywordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["id", "title", "category"]


# 기사 본문 생성(POST)
class ScrapedArticleListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        created_count = 0
        skipped_count = 0
        articles = []

        for item in validated_data:
            keyword = item.pop("keyword_id")

            # 이미 기사 존재하면 스킵
            if Article.objects.filter(keyword=keyword).exists():
                logger.info(f"이미 수집된 키워드입니다. 저장 스킵: {keyword.id}")
                skipped_count += 1
                continue

            # 기사 생성만 수행
            article = Article.objects.create(keyword=keyword, **item)
            created_count += 1
            articles.append(article)

        # 생성/스킵 카운트 저장
        self.created_count = created_count
        self.skipped_count = skipped_count

        return articles


class ScrapedArticleCreateSerializer(serializers.ModelSerializer):
    keyword_id = serializers.PrimaryKeyRelatedField(queryset=Keyword.objects.all())

    class Meta:
        model = Article
        fields = ["keyword_id", "title", "content", "origin_link"]
        list_serializer_class = ScrapedArticleListSerializer
