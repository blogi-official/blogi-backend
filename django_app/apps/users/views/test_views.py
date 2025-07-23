from django.http import Http404, JsonResponse
from django.views import View

from apps.models import User


class GetUserView(View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")

        return JsonResponse(
            {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "profile_image": user.profile_image,
                "provider": user.provider,
                "role": user.role,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
        )
