import os

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.permissions import IsUser

FASTAPI_BASE = os.getenv("FASTAPI_BASE", "http://127.0.0.1:8001")  # 도커 내부 통신 권장
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")  # FastAPI settings.internal_secret_key와 동일


class ArticleJobStartAPIView(APIView):
    permission_classes = [IsUser]  # 관리자만이라면 커스텀 권한으로 교체

    def post(self, request):
        url = f"{FASTAPI_BASE}/api/v1/internal/fetch/article/job"
        headers = {"x-internal-secret": INTERNAL_SECRET}
        try:
            r = requests.post(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            return Response({"detail": str(e)}, status=502)
        try:
            data = r.json()
        except ValueError:
            return Response({"detail": "invalid json from fastapi"}, status=502)
        return Response(data, status=r.status_code)


class ArticleJobStatusAPIView(APIView):
    permission_classes = [IsUser]

    def get(self, request, job_id: str):
        url = f"{FASTAPI_BASE}/api/v1/internal/fetch/article/job/{job_id}"
        headers = {"x-internal-secret": INTERNAL_SECRET}
        try:
            r = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            return Response({"detail": str(e)}, status=502)
        try:
            data = r.json()
        except ValueError:
            return Response({"detail": "invalid json from fastapi"}, status=502)
        return Response(data, status=r.status_code)
