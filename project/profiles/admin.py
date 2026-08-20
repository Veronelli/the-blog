from django.contrib import admin

from profiles.models import Variable


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("identifier", "label", "description")
    search_fields = ("identifier", "label", "description")
    ordering = ("identifier",)
