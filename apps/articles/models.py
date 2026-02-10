from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils import timezone

from apps.core.models import TimestampMixin
from apps.core.validators import validate_image_file


class Article(TimestampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField(help_text="Contenu en Markdown")
    image = models.ImageField(upload_to="articles/images/", blank=True, validators=[validate_image_file])
    category = models.CharField(max_length=100, blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_articles")
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["published", "-published_at"]),
            GinIndex(fields=["search_vector"]),
        ]

    def save(self, *args, **kwargs):
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        if not self.published:
            self.published_at = None
        super().save(*args, **kwargs)
