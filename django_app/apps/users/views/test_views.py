from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from apps.models import User

class GetUserView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")

        data = {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "profile_image": user.profile_image,
            "provider": user.provider,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        return Response(data)