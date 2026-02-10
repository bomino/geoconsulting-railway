from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("created_at", "user", "action", "entity_type", "entity_id")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("action", "entity_type", "details")
    readonly_fields = (
        "user",
        "action",
        "entity_type",
        "entity_id",
        "details",
        "ip_address",
        "user_agent",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
