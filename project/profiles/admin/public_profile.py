from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from profiles.models import PublicProfile


class PublicProfileForm(forms.ModelForm):
    class Meta:
        model = PublicProfile
        fields = (
            "public_username",
            "first_name",
            "last_name",
            "title",
            "subtitle",
            "specialty",
            "short_description",
            "photo_url",
        )


class PublicProfileAdmin(admin.ModelAdmin):
    form = PublicProfileForm
    readonly_fields = ("user",)

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return True

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not PublicProfile.objects.filter(user=request.user).exists()

    def has_change_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        if obj is None:
            return PublicProfile.objects.filter(user=request.user).exists()
        return obj.user_id == request.user.id

    def has_view_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        return self.has_change_permission(request, obj)

    def has_delete_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        return False

    def save_model(
        self,
        request: HttpRequest,
        obj: PublicProfile,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


class SelfServiceAdminSite(admin.AdminSite):
    site_header = "Public profile dashboard"
    site_title = "Public profile dashboard"
    index_title = "Public profile dashboard"

    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_authenticated and request.user.is_active

    def index(
        self, request: HttpRequest, extra_context: dict[str, object] | None = None
    ) -> HttpResponse:
        if not PublicProfile.objects.filter(user=request.user).exists():
            return redirect(f"{self.name}:profiles_publicprofile_add")
        return super().index(request, extra_context)


self_service_admin_site = SelfServiceAdminSite(name="self_service_admin")
self_service_admin_site.register(PublicProfile, PublicProfileAdmin)
