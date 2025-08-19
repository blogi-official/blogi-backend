import os

import requests
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
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsAdmin

# FastAPI 연결 정보 (환경변수)
FASTAPI_BASE = os.getenv("FASTAPI_BASE", "http://127.0.0.1:8001")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET") or os.getenv("INTERNAL_SECRET_KEY") or ""


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
    summary="Clova 콘텐츠 재생성",
    description=(
        "해당 키워드로 이미 생성된 게시글이 있을 경우, FastAPI를 통해 Clova 재생성을 수행합니다.\n"
        "- 내부 시크릿 키 필요 (X-Internal-Secret)\n"
        "- 성공 시 post_id와 상태 반환"
    ),
    responses={
        200: {
            "type": "object",
            "properties": {
                "post_id": {"type": "integer"},
                "status": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "error_message": {"type": "string", "nullable": True},
                "from_cache": {"type": "boolean"},
            },
            "example": {
                "post_id": 112,
                "status": "success",
                "created_at": "2025-08-18T12:34:56.789Z",
                "error_message": None,
                "from_cache": False,
            },
        },
        401: {"description": "관리자 인증 실패"},
        404: {"description": "생성된 게시글 없음 (keyword에 매핑된 GeneratedPost 미존재)"},
        500: {"description": "FastAPI 호출 오류 / 시크릿 미설정"},
    },
)
class ClovaRegenerateAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        # 1) 키워드 존재 확인
        keyword = get_object_or_404(Keyword, id=id)

        if not INTERNAL_SECRET:
            return Response(
                {"detail": "INTERNAL_SECRET(_KEY) 환경변수가 설정되지 않았습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 2) 해당 키워드로 이미 생성된 게시글 찾아 post_id / user_id 획득
        try:
            generated_post = GeneratedPost.objects.get(keyword_id=keyword.id)
        except GeneratedPost.DoesNotExist:
            return Response(
                {"detail": "해당 키워드로 생성된 게시글이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        post_id = generated_post.id
        user_id = generated_post.user_id  # 원 작성자 기준으로 로그 일관성 유지

        # 3) FastAPI 재생성 호출
        url = f"{FASTAPI_BASE}/api/v1/internal/posts/{post_id}/regenerate"
        headers = {"X-Internal-Secret": INTERNAL_SECRET}
        payload = {"user_id": int(user_id)}

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=60)
        except requests.RequestException as e:
            return Response({"detail": f"FastAPI 호출 실패: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            data = r.json()
        except ValueError:
            return Response(
                {"detail": "FastAPI에서 유효하지 않은 JSON을 반환했습니다."}, status=status.HTTP_502_BAD_GATEWAY
            )

        # 4) FastAPI 응답 그대로 반환
        return Response(data, status=r.status_code if r.status_code >= 400 else status.HTTP_200_OK)


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
