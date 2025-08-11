from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custom_admin.serializers.keyword_serializers import (
    AdminKeywordListPageSerializer,
    KeywordDetailSerializer,
    KeywordListItemSerializer,
    KeywordTitleUpdateSerializer,
    KeywordToggleSerializer,
)
from apps.models import GeneratedPost, Keyword
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsAdmin


@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="키워드 공개 상태 토글",
    description=(
        "관리자가 키워드의 공개 여부(`is_active`)를 true/false로 토글합니다.\n\n"
        "- 사용자에게 노출되지 않도록 제어하는 핵심 필드입니다.\n"
        "- 본 요청은 바디 없이 PATCH로 호출되며, 관리자 인증이 필요합니다."
    ),
    responses={
        200: KeywordToggleSerializer,
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        403: {"description": "관리자 권한이 없습니다."},
        404: {"description": "해당 키워드가 존재하지 않습니다."},
    },
)
# 공개/비공개 토글 001
class KeywordToggleView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, id):
        keyword = get_object_or_404(Keyword, id=id)
        keyword.is_active = not keyword.is_active
        keyword.save()

        serializer = KeywordToggleSerializer(keyword)
        return Response(
            {
                "message": "키워드 공개 상태가 변경되었습니다",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="키워드 상세 조회 (기사 + 대표 이미지)",
    description=(
        "관리자가 키워드를 클릭하면 해당 키워드에 매핑된 기사 본문과 대표 이미지를 조회합니다.\n\n"
        "• **title은 `keyword.title`** 을 반환합니다.\n"
        "• 본문(content)과 원문 링크(original_url)는 스크래핑된 **기사(Article)** 기준이며 수정 불가한 정적 데이터입니다.\n"
        "• 대표 이미지는 **최신 활성(Active) 생성글(GeneratedPost)** 에 포함된 최대 3개의 URL을 제공합니다.\n"
        "• 기사 또는 활성 생성글이 없으면 404를 반환합니다."
    ),
    responses={
        200: KeywordDetailSerializer,
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        403: {"description": "관리자 권한이 없습니다."},
        404: {"description": "해당 키워드 또는 기사/활성 생성글 데이터가 존재하지 않습니다."},
    },
    examples=[
        OpenApiExample(
            name="성공 응답 예시",
            value={
                "message": "키워드 상세 조회 성공",
                "data": {
                    "title": "키워드 제목(Keyword.title)",
                    "content": "<p>기사 본문 HTML 또는 텍스트...</p>",
                    "original_url": "https://news.example.com/article/123",
                    "image_1_url": "https://images.example.com/a.jpg",
                    "image_2_url": "https://images.example.com/b.jpg",
                    "image_3_url": None,
                },
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            name="데이터 없음(404)",
            value={"detail": "해당 키워드 또는 기사/활성 생성글 데이터가 존재하지 않습니다."},
            response_only=True,
            status_codes=["404"],
        ),
    ],
)
# 키워드 콘텐츠 상세조회 002
class KeywordDetailAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id: int):
        # Article은 OneToOne(related_name="article")이므로 select_related로 함께 가져오기
        keyword = get_object_or_404(
            Keyword.objects.select_related("article"),
            id=id,
        )

        article = getattr(keyword, "article", None)

        # ✅ 최신의 활성 GeneratedPost 1건을 대표로 선택
        generated_post = (
            GeneratedPost.objects.filter(keyword=keyword, is_active=True).order_by("-created_at", "-id").first()
        )

        # 기존 정책 유지: 둘 중 하나라도 없으면 404
        if not article or not generated_post:
            return Response(
                {"detail": "해당 키워드 또는 기사 데이터가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = KeywordDetailSerializer(
            {
                "keyword": keyword,  #  Serializer에서 keyword.title 사용
                "article": article,
                "generated_post": generated_post,
            }
        )
        return Response(
            {
                "message": "키워드 상세 조회 성공",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# 키워드 제목 수정 003
@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="키워드 제목 수정",
    description=(
        "관리자가 수집된 키워드 제목 텍스트를 수정합니다.\n"
        "- 제목 외 다른 필드는 수정 불가\n"
        "- 수정된 제목은 사용자 리스트에도 즉시 반영됩니다."
    ),
    request=KeywordTitleUpdateSerializer,
    responses={
        200: KeywordTitleUpdateSerializer,
        400: {"description": "제목 필드는 필수이며 유효한 문자열이어야 합니다."},
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        403: {"description": "관리자 권한이 없습니다."},
        404: {"description": "해당 키워드가 존재하지 않습니다."},
    },
)
class KeywordTitleUpdateAPIView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = KeywordTitleUpdateSerializer

    def patch(self, request, id: int):
        keyword = get_object_or_404(Keyword, id=id)
        serializer = self.serializer_class(keyword, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "키워드 제목이 성공적으로 수정되었습니다",
                    "data": {
                        "id": keyword.id,
                        "title": serializer.validated_data["title"],
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 관리자용 키워드 목록조회 api (신설)


@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="키워드 목록 조회 (관리자 전용, 전체)",
    description=(
        "관리자용 전체 키워드 목록 API입니다.\n\n"
        "- `search`: 제목/카테고리 부분일치 검색\n"
        "- `is_active`: true/false 필터\n"
        "- `sort`: created_desc|created_asc|title_asc|title_desc|generated_desc|generated_asc|image_desc|image_asc|lastgen_desc|lastgen_asc\n"
        "- 기본 정렬: created_desc (최신순)\n"
    ),
    parameters=[
        OpenApiParameter(name="search", description="제목/카테고리 부분 검색", required=False, type=str),
        OpenApiParameter(name="is_active", description="활성여부 필터 (true/false)", required=False, type=bool),
        OpenApiParameter(name="sort", description="정렬 키", required=False, type=str),
        OpenApiParameter(name="page", description="페이지 번호 (1-base)", required=False, type=int),
        OpenApiParameter(name="page_size", description="페이지 크기", required=False, type=int),
    ],
    responses={200: AdminKeywordListPageSerializer},
)
class KeywordListAPIView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = KeywordListItemSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        related_name 없는 역참조 경로:
        - GeneratedPost ← Keyword: 'generatedpost' (query 경로), 매니저는 generatedpost_set
        - Image ← Keyword: 'image' (query 경로), 매니저는 image_set
        """
        qs = Keyword.objects.annotate(
            generated_count=Count("generatedpost", distinct=True),  #  OK
            image_count=Count("image", distinct=True),  #  OK
            last_generated_at=Max("generatedpost__created_at"),  #  최근 생성글 시각
        )

        # 검색: 제목/카테고리/소스카테고리
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(category__icontains=search) | Q(source_category__icontains=search)
            )

        # 활성 필터
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            sval = str(is_active).lower()
            if sval in ("true", "1", "yes"):
                qs = qs.filter(is_active=True)
            elif sval in ("false", "0", "no"):
                qs = qs.filter(is_active=False)

        # 정렬
        sort = (self.request.query_params.get("sort") or "created_desc").lower()
        sort_map = {
            "created_desc": "-created_at",
            "created_asc": "created_at",
            "title_asc": "title",
            "title_desc": "-title",
            "generated_desc": "-generated_count",
            "generated_asc": "generated_count",
            "image_desc": "-image_count",
            "image_asc": "image_count",
            "lastgen_desc": "-last_generated_at",
            "lastgen_asc": "last_generated_at",
        }
        return qs.order_by(sort_map.get(sort, "-created_at"))
