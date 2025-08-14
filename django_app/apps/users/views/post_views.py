import tempfile

from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from apps.models import CopyLog, GeneratedPost, User
from apps.users.serializers.post_serializers import (
    CopyLogSerializer,
    GeneratedPostDetailSerializer,
    GeneratedPostListSerializer,
    GeneratedPostUpdateSerializer,
)
from apps.utils.paginations import CustomPageNumberPagination
from apps.utils.permissions import IsUser


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="(User) 마이페이지 콘텐츠 생성 이력 조회",
    description="""
로그인한 사용자가 직접 생성한 블로그 콘텐츠 목록을 반환합니다.

- 최신순 정렬
- 제목, 생성일, 복사횟수 포함
- JWT 인증 필요
""",
    responses={200: GeneratedPostListSerializer},
)
# 마이페이지 생성 콘텐츠 목록 조회(014)
class UserGeneratedPostListAPIView(ListAPIView):
    permission_classes = [IsUser]
    serializer_class = GeneratedPostListSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return GeneratedPost.objects.filter(user=user, is_active=True).order_by("-created_at")


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="(User) 마이페이지 생성 콘텐츠 상세 조회",
    description="""
로그인한 사용자가 본인이 생성한 콘텐츠를 조회합니다.

- 제목, 본문, 이미지 URL, 복사 횟수, 생성일 포함
- 본인이 생성한 글만 조회 가능 (타인의 글: 403)
- 본문은 HTML 포맷입니다.
""",
    responses={200: GeneratedPostDetailSerializer},
)
# 마이페이지 생성 콘텐츠 상세목록 조회(015)
class UserGeneratedPostDetailAPIView(RetrieveAPIView):
    permission_classes = [IsUser]
    serializer_class = GeneratedPostDetailSerializer
    queryset = GeneratedPost.objects.filter(is_active=True)

    def get_object(self):
        post = super().get_object()
        if post.user != self.request.user:

            raise PermissionDenied("타인의 콘텐츠에는 접근할 수 없습니다.")
        return post


@extend_schema(
    tags=["[User] Content - 생성 결과"],
    summary="(User) 생성된 콘텐츠 결과 보기",
    description="""
생성 완료된 블로그 콘텐츠의 상세 HTML 결과를 반환합니다.

- 제목, 본문, 이미지, 복사횟수, 생성일 포함
- 본인 글만 접근 가능 (추후 확장 고려)
- 본문은 HTML 포맷이며, 마크업 기반 렌더링 필요
""",
    responses={200: GeneratedPostDetailSerializer},
)
# 생성결과보기 (003)
class GeneratedPostPublicDetailAPIView(RetrieveAPIView):
    permission_classes = [IsUser]
    serializer_class = GeneratedPostDetailSerializer
    queryset = GeneratedPost.objects.filter(is_active=True)

    def get_object(self):
        post = super().get_object()
        if post.user != self.request.user:
            raise PermissionDenied("다른 사용자가 생성한 콘텐츠에는 접근할 수 없습니다.")
        return post


@extend_schema(
    tags=["[User] Content - 생성 결과"],
    summary="(User) 복사 기능",
    description="사용자가 생성된 콘텐츠를 복사하면 복사 로그를 저장하고 복사 수를 증가시킵니다.",
    responses={200: CopyLogSerializer},
)
# 복사기능 (004)
class PostCopyAPIView(APIView):
    permission_classes = [IsUser]
    serializer_class = CopyLogSerializer

    def post(self, request, id):
        user = request.user
        post = get_object_or_404(GeneratedPost, id=id)

        # 1회만 복사 로그 생성
        copy_log = CopyLog.objects.create(user=user, post=post)

        # copy_count 1 증가 (DB 레벨)
        GeneratedPost.objects.filter(id=post.id).update(copy_count=F("copy_count") + 1)

        serializer = self.serializer_class(copy_log)
        return Response({"message": "복사 기록이 저장되었습니다."}, status=200)


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="(User) PDF 다운로드",
    description="사용자가 생성한 블로그 콘텐츠를 PDF로 저장합니다. 생성자 본인만 접근할 수 있으며, 인증 필요.",
    responses={
        200: OpenApiResponse(description="PDF 파일 다운로드"),
        403: OpenApiResponse(description="본인이 생성한 콘텐츠에만 접근할 수 있습니다."),
        404: OpenApiResponse(description="요청한 자원이 존재하지 않습니다."),
    },
)
# PDF 파일 저장
class PostPDFDownloadAPIView(APIView):
    permission_classes = [IsUser]

    def get(self, request, id):
        user = request.user
        post = get_object_or_404(GeneratedPost, pk=id)

        if post.user != user:
            return Response(
                {"detail": "본인이 생성한 콘텐츠에만 접근할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # HTML → PDF 변환
        html_content = post.content  # HTML 포맷 필드
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            HTML(string=html_content).write_pdf(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

        # PDF 응답 반환
        filename = f"blogi_post_{post.id}.pdf"
        response = FileResponse(open(temp_pdf_path, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="사용자 생성글 삭제",
    description="사용자가 마이페이지에서 본인의 생성 콘텐츠를 개별적으로 삭제합니다. 복구 불가.",
    responses={
        204: None,
        403: {"description": "타인의 글"},
        404: {"description": "존재하지 않음"},
        401: {"description": "JWT 인증 실패"},
    },
)
# 콘텐츠 개별 삭제 (018)
class GeneratedPostDeleteAPIView(APIView):
    permission_classes = [IsUser]

    def delete(self, request, id: int):
        user = request.user
        assert isinstance(user, User)

        try:
            post = GeneratedPost.objects.get(id=id)
        except GeneratedPost.DoesNotExist:
            return Response(
                {"detail": "해당 ID의 콘텐츠가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if post.user_id != user.id:
            return Response(
                {"detail": "다른 사용자가 생성한 콘텐츠는 삭제할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        post.delete()  # CASCADE로 연결된 copy_log, image 자동 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)


# 콘텐츠 생성 상태 변경
@extend_schema(
    tags=["[User] Content - 생성 결과"],
    summary="(User) 생성된 콘텐츠 상태 변경",
    description="사용자가 생성한 콘텐츠에 상태(생성 완료)를 표시합니다.",
    responses={
        200: GeneratedPostUpdateSerializer,
        404: OpenApiResponse(description="해당 ID의 콘텐츠를 찾을 수 없습니다."),
        401: OpenApiResponse(description="JWT 인증이 필요합니다."),
    },
)
class UserGeneratedPostPatchAPIView(APIView):
    permission_classes = [IsUser]
    serializer_class = GeneratedPostUpdateSerializer

    def patch(self, request, post_id: int):
        user = request.user
        try:
            post = GeneratedPost.objects.get(id=post_id, user_id=user.id)
        except GeneratedPost.DoesNotExist:
            return Response({"detail": "해당 ID의 콘텐츠를 찾을 수 없습니다."}, status=404)

        post.is_generated = True
        post.save(update_fields=["is_generated"])

        serializer = self.serializer_class(instance=post)
        return Response(serializer.data, status=200)
