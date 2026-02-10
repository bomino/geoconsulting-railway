from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.models import FAQ, SiteSetting, TeamMember


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


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ("full_name_display", "role", "department", "order", "published")
    list_filter = ("department", "published")
    search_fields = ("first_name", "last_name", "role")
    list_editable = ("order", "published")
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "role", "department", "photo")}),
        ("Contact", {"fields": ("email", "phone")}),
        ("Bio", {"fields": ("bio",)}),
        ("Affichage", {"fields": ("order", "published")}),
    )

    @admin.display(description="Nom complet")
    def full_name_display(self, obj):
        return obj.full_name
