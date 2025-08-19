# apps/users/views/profile.py
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.profile_serializers import (
    UserInterestSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)
from apps.utils.permissions import IsUser


@extend_schema(
    tags=["[User] Profile - 온보딩(닉네임 및 관심사 설정)"],
    summary="(User) 닉네임 및 관심사 설정",
    description="""
최초 회원가입 이후, 사용자가 닉네임과 관심사를 설정하는 온보딩 API입니다.

- 닉네임은 선택값이며, 미입력 시 랜덤으로 생성됩니다.
- 닉네임 중복 시 409 Conflict 응답을 반환합니다.
- 관심사는 최소 1개 이상 필수이며, 다음 enum 중 선택해야 합니다:

    ["연예", "경제", "스포츠", "패션", "자동차", "여행", "맛집"]
""",
    request=UserInterestSerializer,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 3},
                    "nickname": {"type": "string", "example": "블로기유저-2943"},
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["경제", "연예"],
                    },
                },
            },
            description="닉네임 및 관심사 설정 완료",
        ),
        400: OpenApiResponse(description="관심사는 최소 1개 이상 선택해야 합니다."),
        401: OpenApiResponse(description="자격 인증 정보가 포함되어 있지 않습니다."),
        409: OpenApiResponse(description="해당 닉네임은 이미 사용 중입니다."),
    },
)
class UserInterestView(APIView):
    permission_classes = [IsUser]

    def post(self, request):

        serializer = UserInterestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                {"message": "닉네임 및 관심사 설정 완료", "user_info": result},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 프로필 조회
@extend_schema(
    tags=["[User] Profile - 마이페이지"],
    summary="(User) 마이페이지 사용자 정보 조회",
    description="""
로그인한 사용자의 기본 정보를 반환합니다.

- 이메일, 닉네임, 로그인 플랫폼, 가입일시 포함
- JWT 인증 필요
""",
    responses={200: UserProfileSerializer},
)
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({"message": "사용자 정보 조회 성공", "data": serializer.data}, status=200)


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="(User)닉네임 및 관심사 수정",
    description=(
        "사용자가 마이페이지에서 자신의 닉네임과 관심사(category) 정보를 수정합니다.\n\n"
        "- 닉네임은 최대 20자, 중복 불가\n"
        "- 관심사는 최소 1개 이상 필수, enum 값 중 선택\n"
        "- 기존 관심사는 모두 삭제 후 재등록됩니다"
    ),
    request=UserUpdateSerializer,
    responses={
        200: OpenApiResponse(description="수정 성공"),
        401: OpenApiResponse(description="인증 정보가 유효하지 않습니다."),
        403: OpenApiResponse(description="관심사는 최소 1개 이상 선택해야 합니다."),
        409: OpenApiResponse(description="해당 닉네임은 이미 사용 중입니다."),
    },
)
# 닉네임 및 관심사 수정(016)
class UserUpdateView(APIView):
    permission_classes = [IsUser]
    serializer_class = UserUpdateSerializer

    def patch(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.to_representation(user), status=status.HTTP_200_OK)


@extend_schema(
    tags=["[User] MyPage - 생성 이력"],
    summary="(User)회원 탈퇴",
    description=(
        "사용자가 자신의 계정을 영구적으로 탈퇴(삭제)합니다.\n\n"
        "- 연관된 관심사, 생성글, 복사기록 등도 함께 삭제됩니다 (CASCADE)\n"
        "- JWT 인증 필요\n"
        "- 삭제 후 복구는 불가능합니다"
    ),
    responses={
        204: None,
        401: {"description": "JWT 인증 실패"},
        500: {"description": "회원 탈퇴 처리 중 오류 발생"},
    },
)
# 회원탈퇴
class UserDeleteView(APIView):
    permission_classes = [IsUser]

    def delete(self, request):
        try:
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "회원 탈퇴 처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
