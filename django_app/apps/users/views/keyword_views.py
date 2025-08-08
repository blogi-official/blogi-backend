from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Keyword, KeywordClickLog, User
from apps.users.serializers.keyword_serializers import KeywordListSerializer
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsUser
from django.contrib.auth import get_user_model

User = get_user_model()


@extend_schema(
    tags=["[User] Keyword - 콘텐츠"],
    summary="관심사 기반 키워드 조회",
    description=(
        "로그인한 사용자의 관심사를 기준으로 키워드를 우선 정렬하여 반환합니다.\n\n"
        "- 기본 정렬: 관심사 우선 + 최신순 (sort=latest)\n"
        "- 인기순 정렬: 향후 확장 가능 (sort=popular)\n"
        "- 페이지네이션 적용 (page, page_size)"
    ),
    parameters=[
        OpenApiParameter(
            name="sort",
            type=str,
            location=OpenApiParameter.QUERY,
            enum=["latest", "popular"],
            description=(
                "정렬 기준:\n" "- latest: 최신순 + 관심사 우선 (기본값)\n" "- popular: 클릭 수 기반 인기순 (추후 지원)"
            ),
        ),
        OpenApiParameter(
            name="page",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지당 항목 수 (기본 20, 최대 100)",
        ),
    ],
    responses={
        200: OpenApiResponse(description="조회 성공"),
        401: OpenApiResponse(description="인증 필요"),
    },
)

class KeywordListAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = KeywordListSerializer

    def get(self, request: Request) -> Response:
        user = request.user
        qs = Keyword.objects.filter(is_active=True, is_collected=True)
        sort = request.query_params.get("sort", "latest")

        if user.is_authenticated:
            user_categories = user.userinterest_set.values_list("category", flat=True)

            if sort == "popular":
                qs = qs.annotate(clicks=Count("keywordclicklog")).order_by("-clicks", "-collected_at")
                keyword_queryset = qs
            else:
                keyword_queryset = list(qs.filter(category__in=user_categories).order_by("-collected_at")) + list(
                    qs.exclude(category__in=user_categories).order_by("-collected_at")
                )
        else:
            # 비로그인 유저: 최신순만 보여줌
            keyword_queryset = qs.order_by("-collected_at")

        paginator = CustomPageNumberPagination()
        paginated_qs = paginator.paginate_queryset(keyword_queryset, request)
        serializer = KeywordListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)




@extend_schema(
    tags=["[User] Keyword - 콘텐츠"],
    summary="키워드 클릭 기록 등록",
    description="사용자가 키워드를 클릭할 때 클릭 이벤트를 기록합니다.",
    responses={
        201: {"type": "object", "example": {"message": "클릭 로그가 기록되었습니다."}},
        401: {
            "type": "object",
            "example": {"detail": "자격 인증 정보가 포함되어 있지 않습니다."},
        },
        404: {
            "type": "object",
            "example": {"detail": "해당 키워드를 찾을 수 없습니다."},
        },
    },
)
# 키워드 클릭 기록
class KeywordClickLogView(APIView):
    permission_classes = [IsUser]

    def post(self, request, id: int):
        user = request.user

        keyword = get_object_or_404(Keyword, pk=id)

        KeywordClickLog.objects.create(user=user, keyword=keyword)
        from rest_framework import status

        return Response({"message": "클릭 로그가 기록되었습니다."}, status=status.HTTP_201_CREATED)
