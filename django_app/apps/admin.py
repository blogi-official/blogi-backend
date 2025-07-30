from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.models import (
    AdminLog,
    Article,
    ClovaStudioLog,
    CopyLog,
    GeneratedPost,
    Image,
    Keyword,
    KeywordClickLog,
    User,
    UserInterest,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = (
        "id",
        "email",
        "nickname",
        "provider",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("provider", "role", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "nickname")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인정보", {"fields": ("nickname", "profile_image")}),
        ("OAuth 정보", {"fields": ("social_id", "provider")}),
        (
            "권한",
            {
                "fields": (
                    "role",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("중요 날짜", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "nickname",
                    "provider",
                    "role",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category")
    list_filter = ("category",)
    search_fields = ("user__email", "user__nickname")


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "source_category",
        "is_active",
        "is_collected",
        "collected_at",
        "created_at",
    )
    list_filter = ("category", "is_active", "is_collected")
    search_fields = ("title",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "keyword", "title", "origin_link")
    search_fields = ("title", "keyword__title")


@admin.register(GeneratedPost)
class GeneratedPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "keyword",
        "copy_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("title", "user__email", "user__nickname", "keyword__title")


@admin.register(CopyLog)
class CopyLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "copied_at")
    search_fields = ("user__email", "user__nickname", "post__title")


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("id", "admin", "action", "target_type", "target_id", "logged_at")
    search_fields = ("admin__email", "action", "target_type")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "order", "image_url", "collected_at")
    search_fields = ("post__title",)


@admin.register(KeywordClickLog)
class KeywordClickLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "keyword", "clicked_at")
    search_fields = ("user__email", "user__nickname", "keyword__title")


@admin.register(ClovaStudioLog)
class ClovaStudioLogAdmin(admin.ModelAdmin):
    list_display = ("id", "keyword", "status", "response_time_ms", "requested_at")
    list_filter = ("status",)
    search_fields = ("keyword__title",)
