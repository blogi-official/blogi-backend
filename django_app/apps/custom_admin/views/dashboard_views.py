from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count
from django.db.models.functions import Trunc, TruncDate
from django.utils import timezone
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custom_admin.serializers.dashboard_serializers import (
    ClovaStatsSerializer,
    DailyStatsSerializer,
    TopKeywordSerializer,
)
from apps.models import ClovaStudioLog, GeneratedPost, Keyword, KeywordClickLog
from apps.utils.permissions import IsAdmin


@extend_schema(
    tags=["[Admin] 대시보드"],
    summary="최근 7일 콘텐츠 수집/생성 통계",
    description=(
        "관리자가 최근 7일 기준으로 자동 수집된 제목 수와 "
        "사용자 생성된 글 수를 일별로 확인할 수 있습니다.\n\n"
        "- `keyword.collected_at` 및 `generated_post.created_at` 기준\n"
        "- 최신 날짜부터 내림차순 정렬"
    ),
    responses={200: DailyStatsSerializer(many=True)},
)
# KST 기준으로 변경 / 최근 7일 콘텐츠 수집/생성 통계 011
class DailyStatsAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        seoul_tz = ZoneInfo("Asia/Seoul")
        today = now().astimezone(seoul_tz).date()
        start_date = today - timedelta(days=6)

        keyword_qs = (
            Keyword.objects.filter(collected_at__date__range=(start_date, today))
            .annotate(date=TruncDate("collected_at", tzinfo=seoul_tz))
            .values("date")
            .annotate(collected_keywords=Count("id"))
            .order_by("-date")
        )

        post_qs = (
            GeneratedPost.objects.filter(created_at__date__range=(start_date, today))
            .annotate(date=TruncDate("created_at", tzinfo=seoul_tz))
            .values("date")
            .annotate(generated_posts=Count("id"))
            .order_by("-date")
        )

        stats_map = {}

        for item in keyword_qs:
            date = item["date"]
            stats_map[date] = {
                "date": date,
                "collected_keywords": item["collected_keywords"],
                "generated_posts": 0,
            }

        for item in post_qs:
            date = item["date"]
            if date in stats_map:
                stats_map[date]["generated_posts"] = item["generated_posts"]
            else:
                stats_map[date] = {
                    "date": date,
                    "collected_keywords": 0,
                    "generated_posts": item["generated_posts"],
                }

        stats_list = sorted(stats_map.values(), key=lambda x: x["date"], reverse=True)
        serializer = DailyStatsSerializer(stats_list, many=True)
        return Response(
            {"message": "일별 통계 조회 성공", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Admin] 대시보드"],
    summary="인기 키워드 클릭 수 상위 N개 조회",
    description=(
        "관리자가 최근 N일 기준 사용자 클릭 수가 높은 키워드를 조회합니다.\n\n"
        "- 기본 7일 기준 (쿼리 파라미터: days)\n"
        "- 기본 상위 5개 (쿼리 파라미터: limit)\n"
        "- keyword_click_log 테이블을 기준으로 집계됩니다."
    ),
    parameters=[
        OpenApiParameter(
            name="days",
            type=int,
            description="최근 며칠 기준 집계 (기본 7)",
            required=False,
        ),
        OpenApiParameter(
            name="limit",
            type=int,
            description="조회할 상위 개수 (기본 5)",
            required=False,
        ),
    ],
    responses={200: TopKeywordSerializer(many=True)},
)
# 인기 키워드 top 5 통계 012
class TopKeywordAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get("days", 7))
        limit = int(request.query_params.get("limit", 5))
        start_date = now().date() - timedelta(days=days - 1)

        # 클릭 로그 집계
        click_stats = (
            KeywordClickLog.objects.filter(clicked_at__date__gte=start_date)
            .values("keyword_id")
            .annotate(click_count=Count("id"))
            .order_by("-click_count")[:limit]
        )

        # keyword_id → title 매핑
        keyword_ids = [item["keyword_id"] for item in click_stats]
        keyword_map = {k.id: k.title for k in Keyword.objects.filter(id__in=keyword_ids, is_active=True)}

        result = []
        for item in click_stats:
            title = keyword_map.get(item["keyword_id"])
            if title:
                result.append(
                    {
                        "keyword_id": item["keyword_id"],
                        "title": title,
                        "click_count": item["click_count"],
                    }
                )

        serializer = TopKeywordSerializer(result, many=True)
        data = serializer.data

        message = f"{days}일 이내 클릭된 키워드가 없습니다." if not data else "인기 키워드 조회 성공"

        return Response({"message": message, "data": data}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["[Admin] 대시보드"],
    summary="Clova 처리 통계 조회",
    description="관리자가 최근 N일 기준 Clova 처리 성공/실패 통계를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="days",
            description="집계 기준일 범위 (기본값: 7일)",
            required=False,
            type=int,
        ),
    ],
    responses={200: ClovaStatsSerializer},
)
# Clova 처리 결과 통계 013
class ClovaStatsAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get("days", 7))

        since = timezone.now() - timedelta(days=days)

        queryset = ClovaStudioLog.objects.filter(requested_at__gte=since)

        success_count = queryset.filter(status=ClovaStudioLog.ClovaStatus.SUCCESS).count()
        fail_count = queryset.filter(status=ClovaStudioLog.ClovaStatus.FAIL).count()
        total = success_count + fail_count

        if total > 0:
            fail_rate = round((fail_count / total) * 100, 1)
        else:
            fail_rate = 0.0

        data = {
            "total": total,
            "success": success_count,
            "fail": fail_count,
            "fail_rate": fail_rate,
        }

        serializer = ClovaStatsSerializer(data)
        return Response(
            {"message": "Clova 처리 통계 조회 성공", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
