from django.urls import path

from .views_fetch_article_job_proxy import (
    ArticleJobStartAPIView,
    ArticleJobStatusAPIView,
)
from .views_generate_proxy import GenerateProxyAPIView

app_name = "content"

urlpatterns = [
    path("generate/", GenerateProxyAPIView.as_view(), name="generate"),
    #  기사 수집 잡 프록시
    path("articles/job/start/", ArticleJobStartAPIView.as_view(), name="article_job_start"),
    path("articles/job/status/<str:job_id>/", ArticleJobStatusAPIView.as_view(), name="article_job_status"),
]
