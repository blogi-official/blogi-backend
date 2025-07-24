from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("id", "email", "nickname", "provider", "role", "is_staff", "is_active")
    list_filter = ("provider", "role", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "nickname")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인정보", {"fields": ("nickname", "profile_image")}),
        ("OAuth 정보", {"fields": ("social_id", "provider")}),
        ("권한", {"fields": ("role", "is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("중요 날짜", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "nickname", "provider", "role", "is_staff", "is_active"),
            },
        ),
    )
