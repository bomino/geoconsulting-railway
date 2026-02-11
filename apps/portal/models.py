from django.conf import settings
from django.db import models

from apps.core.enums import AccessLevel


class ClientProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_projects")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="client_projects")
    access_level = models.CharField(max_length=10, choices=AccessLevel.choices, default=AccessLevel.VIEW)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="access_grants")
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "project"]

    def __str__(self):
        return f"{self.user} → {self.project} ({self.access_level})"


class ProjectComment(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_comments")
    content = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} on {self.project} ({self.created_at:%Y-%m-%d})"


class Message(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="sent_messages")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="received_messages")
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(max_length=10000)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["to_user", "read"]),
            models.Index(fields=["from_user"]),
        ]
