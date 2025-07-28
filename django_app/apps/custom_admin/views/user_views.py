# apps/custom_admin/views/user_views.py

from datetime import timedelta

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.custom_admin.serializers.user_serializers import (
    AdminLoginSerializer,
    AdminUserGeneratedPostSerializer,
    AdminUserListSerializer,
    AdminUserSummarySerializer,
)
from apps.models import GeneratedPost, User
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsAdmin


@extend_schema(
    tags=["[Admin] 유저 관리"],
    summary="관리자 전용 로그인",
    description="관리자(superuser 또는 role=admin)만 로그인할 수 있으며, access token 유효시간은 6시간입니다.",
    request=AdminLoginSerializer,
    responses={
        200: {"type": "object", "example": {"access": "<access_token>", "refresh": "<refresh_token>"}},
        403: {"description": "관리자 권한이 없습니다."},
        401: {"description": "인증 실패"},
    },
)
class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"detail": "인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        if not (user.role == User.Role.ADMIN or user.is_superuser):
            return Response({"detail": "관리자 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token.set_exp(lifetime=timedelta(hours=6))  # 관리자 전용 6시간 설정

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh),
            }
        )


@extend_schema(
    tags=["[Admin] 유저 관리"],
    summary="가입 유저 목록 조회",
    description="관리자가 가입한 유저의 목록을 이메일, 가입일 기준으로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", type=int, required=False, description="페이지 번호 (기본: 1)"),
        OpenApiParameter(name="size", type=int, required=False, description="한 페이지당 항목 수 (기본: 20)"),
        OpenApiParameter(name="sort", type=str, required=False, description="정렬 필드 (예: created_at)"),
        OpenApiParameter(name="order", type=str, required=False, description="정렬 방식 (asc 또는 desc)"),
        OpenApiParameter(name="email", type=str, required=False, description="이메일 검색 (부분 또는 정확 일치)"),
    ],
    responses={
        200: {
            "description": "가입 유저 목록 조회 성공",
            "examples": [
                {
                    "message": "가입 유저 목록 조회 성공",
                    "data": [
                        {
                            "user_id": 1,
                            "email": "admin@example.com",
                            "provider": "google",
                            "created_at": "2025-07-01T12:00:00",
                        }
                    ],
                    "meta": {"page": 1, "size": 20, "total": 138},
                }
            ],
        },
        401: {"description": "JWT 인증 필요"},
        403: {"description": "관리자 권한이 없습니다"},
    },
)
# 가입 유저 목록 조회 009
class AdminUserListAPIView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserListSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = User.objects.all()
        email = self.request.query_params.get("email")
        sort = self.request.query_params.get("sort", "created_at")
        order = self.request.query_params.get("order", "desc")

        if email:
            queryset = queryset.filter(Q(email__icontains=email))

        if sort not in ["created_at", "email"]:
            sort = "created_at"

        if order == "desc":
            sort = f"-{sort}"

        return queryset.order_by(sort)


@extend_schema(
    tags=["[Admin] 유저 관리"],
    summary="유저별 생성 콘텐츠 이력 조회",
    description=(
        "관리자가 특정 유저의 콘텐츠 생성 이력을 조회할 수 있습니다.\n"
        "- 최신순 정렬 (created_at DESC)\n"
        "- 총 생성 수 및 최근 생성일 함께 반환\n"
        "- limit/offset 기반 페이지네이션"
    ),
    parameters=[
        OpenApiParameter(
            name="limit", type=OpenApiTypes.INT, required=False, description="페이지당 항목 수 (기본: 30)"
        ),
        OpenApiParameter(name="offset", type=OpenApiTypes.INT, required=False, description="시작 인덱스 (기본: 0)"),
    ],
    responses={200: AdminUserGeneratedPostSerializer(many=True)},
)

# 유저별 콘텐츠 생성 이력조회 010
class AdminUserGeneratedPostListAPIView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserGeneratedPostSerializer

    def get(self, request, user_id: int):
        user = get_object_or_404(User, id=user_id)

        limit = int(request.query_params.get("limit", 30))
        offset = int(request.query_params.get("offset", 0))

        queryset = GeneratedPost.objects.filter(user=user).order_by("-created_at")
        total_count = queryset.count()

        first_post = queryset.first()
        latest_created_at = first_post.created_at if first_post else None

        paginated_qs = queryset[offset : offset + limit]
        serializer = self.serializer_class(paginated_qs, many=True)
        user_serializer = AdminUserSummarySerializer(user)

        return Response(
            {
                "message": "유저별 생성 콘텐츠 이력 조회 성공",
                "data": {
                    "user": user_serializer.data,
                    "total_count": total_count,
                    "latest_created_at": latest_created_at,
                    "posts": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )
