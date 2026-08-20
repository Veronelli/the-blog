from django.urls import path

from profiles import views

app_name = "profiles"

urlpatterns = [
    path(
        "profiles/<str:public_username>/",
        views.public_profile,
        name="public_profile",
    ),
]
