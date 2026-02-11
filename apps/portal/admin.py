from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.portal.models import ClientProject, Message, ProjectComment


@admin.register(ClientProject)
class ClientProjectAdmin(ModelAdmin):
    list_display = ("user", "project", "access_level", "last_accessed", "created_at", "created_by")
    list_filter = ("access_level", "project")
    autocomplete_fields = ("user", "project")
    readonly_fields = ("last_accessed",)


@admin.register(ProjectComment)
class ProjectCommentAdmin(ModelAdmin):
    list_display = ("project", "author", "created_at")
    list_filter = ("project", "created_at")
    readonly_fields = ("project", "author", "content", "created_at")


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ("from_user", "to_user", "subject", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("subject", "content")
    readonly_fields = ("from_user", "to_user", "subject", "content", "read", "created_at")
