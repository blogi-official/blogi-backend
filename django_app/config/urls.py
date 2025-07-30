from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("admins/", admin.site.urls),
    path("api/", include("apps.users.urls", namespace="users")),
    path("admin/", include("apps.custom_admin.urls", namespace="custom_admin")),
    path("api/internal/", include("apps.internal.urls", namespace="internal")),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path(
                "api/schema/swagger-ui/",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
            path(
                "api/schema/redoc/",
                SpectacularRedocView.as_view(url_name="schema"),
                name="redoc",
            ),
        ]
