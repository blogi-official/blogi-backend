from django.urls import path

from apps.users.views.test_views import GetUserView

app_name = "tests"

urlpatterns = [
    # USER
    path("<int:user_id>/", GetUserView.as_view(), name="users"),
]
