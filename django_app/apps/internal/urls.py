# apps/internal/urls.py
from django.urls import path

from apps.internal.views.scrap_titles_views import KeywordCreateAPIView

app_name = "internal"

urlpatterns = [
    path("internal/posts/", KeywordCreateAPIView.as_view(), name="keyword-create"),
]
