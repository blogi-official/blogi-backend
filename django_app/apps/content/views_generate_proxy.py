import os

import requests
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.permissions import IsUser

FASTAPI_BASE = os.getenv("FASTAPI_BASE", "http://127.0.0.1:8001")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")


class GenerateProxyAPIView(APIView):
    permission_classes = [IsUser]

    def post(self, request):
        keyword_id = request.data.get("keyword_id")
        if not keyword_id:
            return Response({"detail": "keyword_id is required"}, status=400)

        # FastAPI 내부 generate 엔드포인트
        url = f"{FASTAPI_BASE}/api/v1/internal/generate-clova-post"
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Secret": INTERNAL_SECRET,
        }
        payload = {
            "keyword_id": int(keyword_id),
            "user_id": int(request.user.id),
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=60)
        except requests.RequestException as e:
            return Response({"status": "fail", "error_message": str(e)}, status=502)

        # FastAPI 응답을 그대로 전달
        try:
            data = r.json()
        except ValueError:
            return Response(
                {"status": "fail", "error_message": "invalid json from fastapi"},
                status=502,
            )

        if r.status_code >= 400:
            return Response(data, status=r.status_code)
        return Response(data, status=200)
