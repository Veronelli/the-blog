from django.urls import path

from profiles import views

app_name = "profiles"

urlpatterns = [
    path(
        "dashboard/",
        views.dashboard_profile,
        name="dashboard",
    ),
    path(
        "dashboard/instances/new/",
        views.dashboard_instance_create,
        name="dashboard_instance_create",
    ),
    path(
        "dashboard/instances/<int:pk>/edit/",
        views.dashboard_instance_edit,
        name="dashboard_instance_edit",
    ),
    path(
        "dashboard/instances/<int:pk>/archive/",
        views.dashboard_instance_archive,
        name="dashboard_instance_archive",
    ),
]