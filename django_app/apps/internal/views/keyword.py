from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Keyword


@extend_schema(
    tags=["[Internal] FastAPI ↔ Django - 키워드 관리"],
    summary="키워드 비활성화 처리",
    description="FastAPI에서 수집 실패 시 해당 키워드를 비활성화(is_active=False)로 처리합니다.",
)
class KeywordDeactivateAPIView(APIView):
    permission_classes = [AllowAny]  # 내부 헤더로 인증할 예정 (AllowAny)

    def patch(self, request, id):
        keyword = get_object_or_404(Keyword, id=id)
        keyword.is_active = False
        keyword.save()
        return Response(
            {"message": "키워드가 비활성화 처리되었습니다."},
            status=status.HTTP_200_OK,
        )
