from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custom_admin.serializers.post_serializers import (
    AdminGeneratedPostDeactivateSerializer,
    AdminGeneratedPostDetailSerializer,
    AdminGeneratedPostListSerializer,
    GeneratedPostPreviewSerializer,
)
from apps.models import CopyLog, GeneratedPost, Keyword

# Todo FastAPI(Clova) 호출 함수 - 실제 구현 또는 외부 호출 래퍼 함수
# 현재는 임시 모킹 함수 사용 중
from apps.utils.clova_mock import request_clova_regenerate
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsAdmin


@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="Clova 요약 결과 미리보기",
    description=(
        "관리자가 키워드에 생성된 블로그 스타일 요약 결과를 HTML 형태로 미리 확인할 수 있습니다.\n"
        "- 요약 결과가 없는 경우 204 No Content 반환\n"
        "- 대표 이미지 및 메타 정보 포함"
    ),
    responses={
        200: GeneratedPostPreviewSerializer,
        204: {"description": "Clova 생성 결과가 없습니다."},
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        403: {"description": "관리자 권한이 없습니다."},
    },
)
# Clova 요약 결과 미리보기
class ClovaPreviewAPIView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = GeneratedPostPreviewSerializer

    def get(self, request, id: int):
        # 키워드 존재 여부만 확인해서 404 방지
        get_object_or_404(Keyword, id=id)

        try:
            generated_post = GeneratedPost.objects.get(keyword_id=id)
        except GeneratedPost.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.serializer_class(generated_post)

        return Response(
            {
                "message": "Clova 생성 콘텐츠 미리보기",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Admin] 키워드 관리"],
    summary="Clova 재요약 or 새 글 요청",
    description=(
        "관리자가 Clova 요약 결과가 없거나 부적절한 경우, "
        "AI에게 다시 글을 생성하도록 요청합니다.\n"
        "- 기존 결과 덮어쓰기\n"
        "- FastAPI Clova 호출 기반 처리\n"
        "- 관리자 인증 필요"
    ),
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "post_id": {"type": "integer"},
                        "status": {"type": "string"},
                    },
                },
            },
            "example": {
                "message": "Clova 재생성 요청 완료",
                "data": {"post_id": 112, "status": "success"},
            },
        },
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        404: {"description": "해당 키워드 ID에 대한 기사 본문이 존재하지 않습니다."},
        500: {"description": "서버 오류 발생"},
    },
)
# Clova 재요약 / 새글 요청
class ClovaRegenerateAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        # 키워드 존재 확인
        keyword = get_object_or_404(Keyword, id=id)

        try:
            # Todo FastAPI(Clova Studio) 호출 - 실제 비동기 작업 또는 sync 래퍼 함수 사용 권장
            # 현재는 임시 모킹 함수 사용 중
            post_id, status_str = request_clova_regenerate(keyword.id)
        except Exception:
            return Response(
                {"detail": "Clova 요약 요청 처리 중 서버 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Clova 재생성 요청 완료",
                "data": {"post_id": post_id, "status": status_str},
            },
            status=status.HTTP_200_OK,
        )


# 사용자 생성 콘텐츠 목록조회 006
@extend_schema(
    tags=["[Admin] 생성 콘텐츠 관리"],
    summary="사용자 생성 콘텐츠 목록 조회",
    description=(
        "관리자가 전체 사용자 생성 콘텐츠 목록을 조회할 수 있습니다.\n"
        "- 이메일 및 제목으로 부분 검색 가능\n"
        "- 최신순 정렬\n"
        "- 페이지네이션 포함"
    ),
    parameters=[
        OpenApiParameter(name="page", type=int, description="페이지 번호 (기본: 1)"),
        OpenApiParameter(name="size", type=int, description="페이지 크기 (기본: 20)"),
        OpenApiParameter(name="email", type=str, description="사용자 이메일(부분 검색)"),
        OpenApiParameter(name="title", type=str, description="콘텐츠 제목(부분 검색)"),
    ],
    responses={200: AdminGeneratedPostListSerializer(many=True)},
)
# 사용자 생성 콘텐츠 목록조회 006
class GeneratedPostListAPIView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminGeneratedPostListSerializer

    def get(self, request):
        queryset = GeneratedPost.objects.select_related("user").order_by("-created_at")

        email = request.query_params.get("email")
        title = request.query_params.get("title")

        if email:
            queryset = queryset.filter(user__email__icontains=email)
        if title:
            queryset = queryset.filter(title__icontains=title)

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = self.serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["[Admin] 생성 콘텐츠 관리"],
    summary="사용자 생성 콘텐츠 상세 조회",
    description=(
        "관리자가 사용자가 생성한 블로그 콘텐츠를 상세 조회합니다.\n"
        "- HTML 콘텐츠 포함\n"
        "- 이미지/복사횟수/작성일 포함"
    ),
    responses={
        200: AdminGeneratedPostDetailSerializer,
        401: {"description": "관리자 권한이 없습니다."},
        404: {"description": "존재하지 않는 콘텐츠입니다."},
    },
)
# 사용자 생성 콘텐츠 상세조회 007
class GeneratedPostDetailAPIView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminGeneratedPostDetailSerializer

    def get(self, request, id):
        post = get_object_or_404(GeneratedPost, id=id)
        serializer = self.serializer_class(post)
        return Response(
            {
                "message": "콘텐츠 상세 조회 성공",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Admin] 생성 콘텐츠 관리"],
    summary="콘텐츠 비공개 또는 삭제 처리",
    description="관리자가 부적절한 콘텐츠를 비공개 처리하거나 완전 삭제할 수 있습니다.",
    request=AdminGeneratedPostDeactivateSerializer,
    responses={
        200: {"type": "object", "example": {"message": "콘텐츠 비공개 처리 완료"}},
        204: None,
        400: {"description": "is_active 값 오류"},
        401: {"description": "인증 정보 없음"},
        403: {"description": "관리자 권한 없음"},
        404: {"description": "해당 콘텐츠가 존재하지 않음"},
        500: {"description": "서버 오류"},
    },
)
# 사용자 생성 콘텐츠 비공개 / 삭제처리 008
class GeneratedPostDeactivateOrDeleteAPIView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, id):
        post = get_object_or_404(GeneratedPost, id=id)

        serializer = AdminGeneratedPostDeactivateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        post.is_active = False
        post.save()

        return Response(
            {"message": "콘텐츠 비공개 처리 완료"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id):
        post = get_object_or_404(GeneratedPost, id=id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
