from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin

from apps.articles.models import Article


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ("title", "category", "published", "published_at", "created_at")
    list_filter = ("published", "category")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if obj.published and not obj.published_at:
            obj.published_at = timezone.now()
        if not obj.published:
            obj.published_at = None
        super().save_model(request, obj, form, change)
