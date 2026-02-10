from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.models import FAQ, SiteSetting


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ("question", "category", "order", "published", "created_at")
    list_filter = ("category", "published")
    list_editable = ("order", "published")
    search_fields = ("question", "answer")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ("key", "updated_at")
    search_fields = ("key",)
    readonly_fields = ("key",)
