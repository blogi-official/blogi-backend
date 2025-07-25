from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custom_admin.serializers.keyword_serializers import (
    KeywordDetailSerializer,
    KeywordTitleUpdateSerializer,
    KeywordToggleSerializer,
)
from apps.models import Keyword
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
    summary="키워드 기사 상세 조회",
    description=(
        "관리자가 키워드를 클릭하면 해당 키워드에 매핑된 기사 본문 및 대표 이미지를 확인할 수 있습니다.\n\n"
        "- 본문은 사전 스크래핑된 정적 데이터이며 수정 불가능합니다.\n"
        "- 대표 이미지는 생성된 콘텐츠에 포함된 최대 3개의 URL입니다."
    ),
    responses={
        200: KeywordDetailSerializer,
        401: {"description": "관리자 인증 정보가 유효하지 않습니다."},
        403: {"description": "관리자 권한이 없습니다."},
        404: {"description": "해당 키워드 또는 기사 데이터가 존재하지 않습니다."},
    },
)
# 키워드 콘텐츠 상세조회 002
class KeywordDetailAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id: int):
        keyword = get_object_or_404(Keyword, id=id)
        article = getattr(keyword, "article", None)
        generated_post = getattr(keyword, "generatedpost", None)

        if not article or not generated_post:
            return Response(
                {"detail": "해당 키워드 또는 기사 데이터가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = KeywordDetailSerializer(
            {
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
