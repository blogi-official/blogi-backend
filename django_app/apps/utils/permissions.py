from rest_framework.permissions import BasePermission

from apps.models import User


class IsUser(BasePermission):
    """
    일반 사용자 (User.Role.USER) 만 접근 가능
    """

    message = "사용자 권한이 필요합니다."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.USER)


class IsAdmin(BasePermission):
    """
    관리자 (User.Role.ADMIN 또는 is_superuser) 만 접근 가능
    """

    message = "관리자 권한이 필요합니다."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == User.Role.ADMIN or user.is_superuser))
