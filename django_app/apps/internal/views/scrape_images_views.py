from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny  # 내부 API니까 AllowAny로
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.internal.serializers.scrape_images_serializers import (
    ImageSaveRequestSerializer,
    KeywordImageTargetSerializer,
)
from apps.models import Article, Image, Keyword


@extend_schema(
    tags=["[Internal] Keyword - 내부 연동"],
    summary="이미지 수집 대상 키워드 1건 조회",
    description=(
        "FastAPI에서 이미지 수집을 위한 키워드 1건을 반환합니다.\n\n"
        "- `is_collected=False` 조건\n"
        "- `article`가 이미 수집되어 있는 키워드만 대상\n"
        "- 정렬 기준: `created_at` 오름차순 (가장 오래된 것부터)\n"
        "- 대상이 없으면 404 반환"
    ),
    responses={200: KeywordImageTargetSerializer, 404: {"description": "대상 없음"}},
)
class KeywordNextImageTargetAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = KeywordImageTargetSerializer

    def get(self, request):
        keyword = Keyword.objects.filter(is_collected=False, article__isnull=False).order_by("created_at").first()

        if not keyword:
            return Response({"detail": "수집 대상 키워드가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(keyword)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["[Internal] Keyword - 내부 연동"],
    summary="대표 이미지 저장",
    description="FastAPI가 수집한 이미지 URL들을 저장합니다. 최대 3개까지만 허용되며 keyword_id 기준으로 저장됩니다.",
    request=ImageSaveRequestSerializer,
    responses={
        201: {"description": "저장 성공"},
        400: {"description": "잘못된 요청"},
        404: {"description": "키워드 없음"},
    },
)
class ImageSaveAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ImageSaveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keyword_id = serializer.validated_data["keyword_id"]
        images = serializer.validated_data["images"]

        try:
            keyword = Keyword.objects.get(id=keyword_id)
        except Keyword.DoesNotExist:
            return Response({"detail": "해당 키워드가 존재하지 않습니다."}, status=404)

        for idx, url in enumerate(images[:3]):
            Image.objects.create(
                keyword=keyword,  # ForeignKey 추가
                post=None,  # 아직 생성 글 없음
                image_url=url,
                order=idx + 1,
                description=None,
                collected_at=now(),
            )

        return Response({"detail": "이미지가 저장되었습니다."}, status=201)


@extend_schema(
    tags=["[Internal] Keyword - 내부 연동"],
    summary="키워드 수집 완료 처리",
    description="이미지 수집이 완료된 키워드의 is_collected=True로 설정합니다.",
    responses={200: {"description": "수집 완료"}, 404: {"description": "키워드 없음"}},
)
class KeywordMarkCollectedAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, id):
        try:
            keyword = Keyword.objects.get(id=id)
        except Keyword.DoesNotExist:
            return Response({"detail": "키워드가 존재하지 않습니다."}, status=404)

        keyword.is_collected = True
        keyword.collected_at = now()
        keyword.save()

        return Response({"detail": "수집 완료로 처리되었습니다."}, status=200)
