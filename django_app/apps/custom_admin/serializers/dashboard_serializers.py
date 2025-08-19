from rest_framework import serializers


# 일별 콘텐츠 수집/생성 통계 011
class DailyStatsSerializer(serializers.Serializer):
    date = serializers.DateField()
    collected_keywords = serializers.IntegerField()
    generated_posts = serializers.IntegerField()


# 인기 키워드 top 5 통계 012
class TopKeywordSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    title = serializers.CharField()
    click_count = serializers.IntegerField()


# Clova 처리 결과 통계 013
class ClovaStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    success = serializers.IntegerField()
    fail = serializers.IntegerField()  # type: ignore[assignment]
    fail_rate = serializers.FloatField()
