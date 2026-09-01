from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Client


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get("secret"):
            self.initial["secret"] = Client.generate_secret()


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = ("name", "domain", "is_active", "created_at")
    list_filter = ("is_active", "groups")
    search_fields = ("name", "domain")
    ordering = ("-created_at",)
    filter_horizontal = ("groups", "permissions")
    readonly_fields = ()

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if "secret" in fields:
            fields.remove("secret")
            fields.insert(2, "secret")
        return fields
