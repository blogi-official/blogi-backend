from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.internal.serializers.scrap_titles_serializers import (
    ScrapedKeywordBulkCreateSerializer,
)


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="스크랩 키워드 생성",
    description="FastAPI에서 수집한 키워드를 저장하고, 생성/중복 개수를 반환합니다.",
    examples=[
        OpenApiExample(
            name="스크랩 키워드 리스트 예시",
            value=[
                {
                    "title": "string",
                    "category": "string",
                    "source_category": "string",
                    "collected_at": "2025-07-30T08:28:17.958Z",
                    "is_collected": True,
                }
            ],
            request_only=True,
        ),
    ],
)
class KeywordCreateAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ScrapedKeywordBulkCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "message": f"총 {result['total_count']}건의 키워드가 수집되었습니다.",
                "created_count": result["created_count"],
                "updated_count": result["updated_count"],
            },
            status=status.HTTP_201_CREATED,
        )
