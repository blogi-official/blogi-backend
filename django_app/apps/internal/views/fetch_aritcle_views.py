from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from apps.models import Keyword, Article

from apps.internal.serializers.fetch_article_serializers import (
    KeywordListSerializer, ScrapedArticleCreateSerializer
)



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
        키워드 전체 조회 API
        """
        try:
            keywords = Keyword.objects.order_by("-created_at")
        except Keyword.DoesNotExist:
            return Response({"detail": "키워드가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(keywords, many=True)
        return Response({"message": "키워드 목록 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)



@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="스크랩 기사 본문 생성",
    description="FastAPI에서 수집한 기사 본문를 저장하고, 생성/중복 개수를 반환합니다.",
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
        return Response(
            {"message": "기사 본문이 수집되었습니다."
                # "message": f"총 {total_count}건의 기사 본문가 수집되었습니다.",
                # "created_count": created_count,
                # "skipped_count": skipped_count,
            },
            status=status.HTTP_201_CREATED,
        )
        # created_count = 0
        # skipped_count = 0
        #
        # for item_data in serializer.validated_data:
        #     article, created = Article.objects.get_or_create(
        #         keyword_id=item_data['keyword_id'],
        #         defaults={
        #             'title': item_data['title'],
        #             'content': item_data['content'],
        #             'origin_link': item_data['origin_link'],
        #         }
        #     )
        #     if created:
        #         created_count += 1
        #     else:
        #         skipped_count += 1
        #
        # total_count = created_count + skipped_count
