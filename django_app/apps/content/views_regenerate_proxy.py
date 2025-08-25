import os

import requests
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.permissions import IsAdmin

# FastAPI 베이스 URL
# 예)
#  - 로컬 단독실행: http://127.0.0.1:8001
#  - Docker: http://fastapi:8000/fastapi
FASTAPI_BASE = os.getenv("FASTAPI_BASE", "http://127.0.0.1:8001")

# 내부 시크릿: INTERNAL_SECRET 없으면 INTERNAL_SECRET_KEY로 폴백
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET") or os.getenv("INTERNAL_SECRET_KEY") or ""


class RegenerateProxyAPIView(APIView):
    permission_classes = [IsAdmin]  #

    def post(self, request, post_id: int):
        if not INTERNAL_SECRET:
            return Response(
                {
                    "status": "fail",
                    "error_message": "INTERNAL_SECRET(_KEY) 환경변수가 비어 있습니다.",
                },
                status=500,
            )

        url = f"{FASTAPI_BASE}/api/v1/internal/posts/{post_id}/regenerate"
        headers = {"X-Internal-Secret": INTERNAL_SECRET}
        # 관리자 액션이지만, FastAPI는 user_id를 요구함 → 기존 글의 user_id가 이상적이나,
        # content 레이어에선 request.user.id(관리자)로 전달하는 프록시 역할만 수행.
        payload = {"user_id": int(getattr(request.user, "id", 0) or 0)}

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=60)
        except requests.RequestException as e:
            return Response({"status": "fail", "error_message": str(e)}, status=502)

        # FastAPI 응답 전달
        try:
            data = r.json()
        except ValueError:
            return Response(
                {"status": "fail", "error_message": "invalid json from fastapi"},
                status=502,
            )

        return Response(data, status=r.status_code if r.status_code >= 400 else 200)
