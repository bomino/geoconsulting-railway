from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.portal.models import ClientProject, Message


@admin.register(ClientProject)
class ClientProjectAdmin(ModelAdmin):
    list_display = ("user", "project", "access_level", "created_at", "created_by")
    list_filter = ("access_level", "project")
    autocomplete_fields = ("user", "project")


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ("from_user", "to_user", "subject", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("subject", "content")
    readonly_fields = ("from_user", "to_user", "subject", "content", "read", "created_at")
