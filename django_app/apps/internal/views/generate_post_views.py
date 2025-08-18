import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.internal.serializers.generate_post_serializers import (
    ArticleWithImagesSerializer,
    ClovaFailLogSerializer,
    ClovaSuccessLogSerializer,
    InternalGeneratedPostCreateSerializer,
    InternalGeneratedPostDetailSerializer,
    InternalGeneratedPostUpdateSerializer,
)
from apps.models import Article, ClovaStudioLog, GeneratedPost, Image, Keyword, User
from config.settings import INTERNAL_SECRET

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="기사 + 이미지 통합 조회",
    description="FastAPI에서 Clova 생성을 위해 keyword_id로 기사 본문과 이미지 URL 리스트를 조회합니다.",
    responses=ArticleWithImagesSerializer,
    examples=[
        OpenApiExample(
            name="기사 + 이미지 응답 예시",
            value={
                "title": "2025 여름을 강타할 패션 키워드",
                "content": "2025년 여름, 가장 주목받는 패션 스타일은...",
                "image_urls": [
                    "https://cdn.blogi.com/1.jpg",
                    "https://cdn.blogi.com/2.jpg",
                    "https://cdn.blogi.com/3.jpg",
                ],
            },
            response_only=True,
        )
    ],
)
# 기사 + 이미지 통합 조회 005
class InternalArticleDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, keyword_id: int):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        keyword = Keyword.objects.select_related("article").get(id=keyword_id)
        if not keyword:
            return JsonResponse({"detail": "해당 키워드는 존재하지 않습니다."}, status=404)

        article = getattr(keyword, "article", None)
        if not article:
            return JsonResponse({"detail": "해당 키워드의 기사 본문이 없습니다."}, status=404)

        images = Image.objects.filter(keyword_id=keyword_id).order_by("order")[:3]
        image_urls = [img.image_url for img in images]

        if not image_urls:
            logger.warning(f"Keyword id={keyword.id}에 이미지가 없습니다.")

        data = {
            "title": keyword.title,
            "content": article.content,
            "image_urls": image_urls,
        }

        return Response(data, status=200)


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="Clova 생성 결과 저장",
    description="FastAPI가 Clova Studio 생성 결과를 Django로 전송하여 저장합니다.",
    request=InternalGeneratedPostCreateSerializer,
    responses={
        201: OpenApiExample(
            "저장 성공 예시",
            value={"post_id": 101, "created_at": "2025-08-05T12:30:00"},
            response_only=True,
        )
    },
)
# Clova 생성 결과 저장
class InternalGeneratedPostCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 내부 인증
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = InternalGeneratedPostCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "필수 필드 누락 또는 잘못된 형식입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        keyword = get_object_or_404(Keyword, id=data["keyword_id"])
        user = get_object_or_404(User, id=data["user_id"])

        post = GeneratedPost.objects.create(
            user=user,
            keyword=keyword,
            title=data["title"],
            content=data["content"],
            image_1_url=data.get("image_1_url"),
            image_2_url=data.get("image_2_url"),
            image_3_url=data.get("image_3_url"),
            is_generated=False,
            created_at=now(),
        )

        return Response(
            {"post_id": post.id, "created_at": post.created_at.isoformat()},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="Clova 성공 로그 저장",
    description="FastAPI가 Clova Studio 생성에 성공한 경우, Django에 성공 로그를 저장합니다.",
    request=ClovaSuccessLogSerializer,
    responses={
        201: OpenApiExample(
            "성공 로그 저장 예시",
            value={"log_id": 555, "status": "success"},
            response_only=True,
        )
    },
)
# Clova 성공 로그 저장 006
class ClovaSuccessLogCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ClovaSuccessLogSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        keyword = get_object_or_404(Keyword, id=data["keyword_id"])

        log = ClovaStudioLog.objects.create(
            keyword=keyword,
            status=ClovaStudioLog.ClovaStatus.SUCCESS,
            response_time_ms=data.get("response_time_ms"),
            requested_at=now(),
        )

        return Response({"log_id": log.id, "status": log.status}, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="Clova 실패 로그 저장",
    description="FastAPI가 Clova Studio 생성에 실패한 경우, Django에 실패 로그를 저장합니다.",
    request=ClovaFailLogSerializer,
    responses={
        201: OpenApiExample(
            "실패 로그 저장 예시",
            value={"log_id": 999, "status": "fail"},
            response_only=True,
        )
    },
)
# Clova 실패 로그 저장
class ClovaFailLogCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ClovaFailLogSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        keyword = get_object_or_404(Keyword, id=data["keyword_id"])

        log = ClovaStudioLog.objects.create(
            keyword=keyword,
            status=ClovaStudioLog.ClovaStatus.FAIL,
            error_message=data["error_message"],
            response_time_ms=data.get("response_time_ms"),
            requested_at=now(),
        )

        return Response({"log_id": log.id, "status": log.status}, status=status.HTTP_201_CREATED)


# 기존 유저가 글생성 요청했을때 프리뷰 반환
@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="Clova 생성글 중복 확인",
    description=(
        "FastAPI가 Clova Studio 콘텐츠 생성을 시도하기 전에, "
        "해당 유저가 이미 같은 키워드로 글을 생성했는지 확인합니다.\n\n"
        "- 중복된 글이 있을 경우: `200 OK` + `post_id`, `created_at` 반환\n"
        "- 중복 글이 없을 경우: `204 No Content`\n"
        "- 인증 실패 시: `401`"
    ),
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            required=True,
            location=OpenApiParameter.QUERY,
            description="유저 ID",
        ),
        OpenApiParameter(
            name="keyword_id",
            type=int,
            required=True,
            location=OpenApiParameter.QUERY,
            description="키워드 ID",
        ),
    ],
    responses={
        200: OpenApiExample(
            "중복 글 존재",
            value={"post_id": 123, "created_at": "2025-08-05T13:00:00"},
            response_only=True,
        ),
        204: OpenApiExample("중복 없음", value=None, response_only=True),
        401: OpenApiExample("내부 인증 실패", value={"detail": "내부 인증 실패"}, response_only=True),
    },
)
class GeneratedPostPreviewAPIView(APIView):
    permission_classes = [AllowAny]  # 내부 인증만 수행

    def post(self, request):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.data.get("user_id")
        keyword_id = request.data.get("keyword_id")

        if not user_id or not keyword_id:
            return Response({"detail": "user_id, keyword_id는 필수입니다."}, status=400)

        try:
            post = GeneratedPost.objects.get(user_id=user_id, keyword_id=keyword_id)
            return Response(
                {
                    "post_id": post.id,
                    "created_at": post.created_at.isoformat(),
                },
                status=status.HTTP_200_OK,
            )
        except GeneratedPost.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 콘텐츠 동기화"],
    summary="Clova 생성 결과 덮어쓰기 (재생성)",
    description="FastAPI가 기존 글을 재생성한 결과를 Django로 전송하여 덮어씁니다.",
    request=InternalGeneratedPostUpdateSerializer,
    responses={200: ...},  # 성공 응답 스키마 정의
)
class InternalRegeneratedPostAPIView(APIView):
    permission_classes = [AllowAny]

    # clova로 생성된 게시글 조회
    def get(self, request, post_id: int):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        post = get_object_or_404(GeneratedPost, id=post_id)
        serializer = InternalGeneratedPostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # clova로 생성된 게시글 수정(재생성)
    def patch(self, request, post_id: int):
        secret = request.headers.get("X-Internal-Secret")
        if secret != INTERNAL_SECRET:
            return Response({"detail": "내부 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        post = get_object_or_404(GeneratedPost, id=post_id)
        serializer = InternalGeneratedPostUpdateSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_post = serializer.save()

        return Response(
            {"post_id": updated_post.id, "created_at": updated_post.created_at.isoformat()},
            status=status.HTTP_200_OK,
        )
