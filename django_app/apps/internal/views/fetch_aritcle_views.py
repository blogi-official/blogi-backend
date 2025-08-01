from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.internal.serializers.fetch_article_serializers import (
    KeywordListSerializer,
    ScrapedArticleCreateSerializer,
)
from apps.models import Article, Keyword


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="스크랩 키워드 조회",
    description="FastAPI에서 수집하여 저장한 키워드를 조회하고, 목록을 반환합니다.",
)
class KeywordListAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = KeywordListSerializer

    def get(self, request: Request) -> Response:
        """
        키워드 조회 API (기사 본문 수집 대상 1건)
        """
        keyword = Keyword.objects.filter(is_collected=False, article__isnull=True).order_by("created_at").first()

        if not keyword:
            return Response(
                {"detail": "키워드가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(keyword)
        return Response(
            {"message": "키워드 조회 완료", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="스크랩 기사 본문 생성",
    description="FastAPI에서 수집한 기사 본문을 저장하고, 생성/중복 개수를 반환합니다.",
    examples=[
        OpenApiExample(
            name="스크랩 기사 리스트 예시",
            value=[
                {
                    "keyword_id": 123,
                    "title": "오늘의 기사",
                    "origin_link": "https://example.com",
                    "content": "기사 본문 내용입니다",
                }
            ],
            request_only=True,
        )
    ],
)
class ArticleCreateAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ScrapedArticleCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"message": "잘못된 데이터", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()

        created_count = getattr(serializer, "created_count", 0)
        skipped_count = getattr(serializer, "skipped_count", 0)

        return Response(
            {
                "message": "기사 본문이 수집되었습니다.",
                "created_count": created_count,
                "skipped_count": skipped_count,
            },
            status=status.HTTP_201_CREATED,
        )
