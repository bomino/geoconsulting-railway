from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse

from apps.core.enums import ProjectCategory, ProjectStatus
from apps.core.models import TimestampMixin
from apps.core.validators import validate_document_file, validate_image_file


class Project(TimestampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Contenu en Markdown")
    category = models.CharField(max_length=20, choices=ProjectCategory.choices)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.EN_COURS)
    location = models.CharField(max_length=255, blank=True)
    client_name = models.CharField(max_length=255, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="projects/images/", blank=True, validators=[validate_image_file])
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_projects")
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "published"]),
            GinIndex(fields=["search_vector"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})


class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="projects/documents/%Y/%m/", validators=[validate_document_file])
    category = models.CharField(max_length=100, blank=True, help_text="Plans, Rapports, Photos, etc.")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.project.title})"

    @property
    def size_display(self):
        size = self.file.size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
