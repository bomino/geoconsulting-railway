from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.projects.models import Project, ProjectDocument


class ProjectDocumentInline(TabularInline):
    model = ProjectDocument
    extra = 1
    fields = ("title", "description", "file", "category", "uploaded_by")
    readonly_fields = ("uploaded_by",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.action(description="Publier les projets sélectionnés")
def bulk_publish(modeladmin, request, queryset):
    queryset.update(published=True)


@admin.action(description="Dépublier les projets sélectionnés")
def bulk_unpublish(modeladmin, request, queryset):
    queryset.update(published=False)


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("title", "category", "status", "published", "year", "created_at")
    list_filter = ("category", "status", "published", "year")
    search_fields = ("title", "description", "location")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectDocumentInline]
    actions = [bulk_publish, bulk_unpublish]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(ModelAdmin):
    list_display = ("title", "project", "category", "uploaded_by", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "description")
