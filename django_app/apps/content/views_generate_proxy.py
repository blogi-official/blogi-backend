import os
from datetime import datetime, time, timedelta

import requests
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.permissions import IsUser
from apps.models import GeneratedPost  # 성공 생성 수만 사용

FASTAPI_BASE = os.getenv("FASTAPI_BASE", "http://127.0.0.1:8001")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")
DAILY_LIMIT = int(os.getenv("DAILY_GENERATE_LIMIT", "3"))


class GenerateProxyAPIView(APIView):
    permission_classes = [IsUser]

    def post(self, request):
        keyword_id = request.data.get("keyword_id")
        if not keyword_id:
            return Response({"detail": "keyword_id is required"}, status=400)

        user = request.user

        # ── 오늘(KST) 구간 ───────────────────────────────────────────────
        today = timezone.localdate()
        start = timezone.make_aware(datetime.combine(today, time.min))
        end = start + timedelta(days=1)

        # ✅ 성공한 생성 수로만 카운트
        used_posts = GeneratedPost.objects.filter(
            user=user, created_at__gte=start, created_at__lt=end
        ).count()

        if used_posts >= DAILY_LIMIT:
            return Response(
                {
                    "status": "fail",
                    "error_code": "DAILY_LIMIT_EXCEEDED",
                    "detail": f"오늘은 {DAILY_LIMIT}회까지만 생성할 수 있어요.",
                    "error_message": f"오늘은 {DAILY_LIMIT}회까지만 생성할 수 있어요.",
                    "limit": DAILY_LIMIT,
                    "today_count": used_posts,
                    "remaining": 0,
                },
                status=429,
            )

        # ── FastAPI 내부 엔드포인트로 프록시 ──────────────────────────────
        url = f"{FASTAPI_BASE}/api/v1/internal/generate-clova-post"
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Secret": INTERNAL_SECRET,
        }
        payload = {
            "keyword_id": int(keyword_id),
            "user_id": int(user.id),
        }

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

        if r.status_code >= 400:
            return Response(data, status=r.status_code)
        return Response(data, status=200)
