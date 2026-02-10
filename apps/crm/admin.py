from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.crm.models import AssignmentRule, EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(ModelAdmin):
    list_display = ("name", "subject", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "subject", "body")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssignmentRule)
class AssignmentRuleAdmin(ModelAdmin):
    list_display = ("name", "keywords_display", "assigned_user", "priority", "active")
    list_filter = ("active",)
    list_editable = ("priority", "active")
    search_fields = ("name",)

    @admin.display(description="Mots-clés")
    def keywords_display(self, obj):
        if isinstance(obj.keywords, list):
            return ", ".join(obj.keywords)
        return str(obj.keywords)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
