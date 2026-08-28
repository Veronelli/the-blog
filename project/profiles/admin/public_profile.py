from django import forms
from django.contrib import admin
from django.http import HttpRequest

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


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    form = PublicProfileForm
    add_form_template = "admin/profiles/publicprofile/change_form.html"
    change_form_template = "admin/profiles/publicprofile/change_form.html"

    def get_queryset(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return super().get_queryset(request).none()
        return super().get_queryset(request).filter(user_id=request.user.id)

    def has_module_permission(self, request: HttpRequest) -> bool:
        user = request.user
        return user.is_authenticated and user.is_staff

    def has_add_permission(self, request: HttpRequest) -> bool:
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        return not PublicProfile.objects.filter(user_id=user.id).exists()

    def has_change_permission(
        self, request: HttpRequest, obj: PublicProfile | None = None
    ) -> bool:
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        if obj is None:
            return PublicProfile.objects.filter(user_id=user.id).exists()
        return obj.user_id == user.id

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
