from django.urls import path

from .views_generate_proxy import GenerateProxyAPIView

app_name = "content"

urlpatterns = [
    path("generate/", GenerateProxyAPIView.as_view(), name="generate"),
]
