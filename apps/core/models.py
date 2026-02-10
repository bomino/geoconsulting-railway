from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image

from apps.core.enums import Department
from apps.core.validators import validate_image_file

TEAM_PHOTO_MAX_SIZE = 100


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])

    class Meta:
        abstract = True


class SiteSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    image = models.ImageField(upload_to="site/", blank=True, validators=[validate_image_file])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


class FAQCategory(models.TextChoices):
    GENERAL = "general", "Général"
    SERVICES = "services", "Nos Services"
    PROJETS = "projets", "Projets & Références"
    CLIENTS = "clients", "Espace Client"
    CONTACT = "contact", "Contact & Devis"


class FAQ(TimestampMixin):
    question = models.CharField(max_length=500)
    answer = models.TextField(help_text="Contenu en Markdown")
    category = models.CharField(
        max_length=20,
        choices=FAQCategory.choices,
        default=FAQCategory.GENERAL,
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage dans la catégorie",
    )
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class TeamMember(TimestampMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    department = models.CharField(max_length=20, choices=Department.choices)
    photo = models.ImageField(upload_to="team/", blank=True, validators=[validate_image_file])
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["department", "order", "last_name"]
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.width > TEAM_PHOTO_MAX_SIZE or img.height > TEAM_PHOTO_MAX_SIZE:
                img.thumbnail((TEAM_PHOTO_MAX_SIZE, TEAM_PHOTO_MAX_SIZE), Image.LANCZOS)
                buf = BytesIO()
                fmt = "JPEG" if self.photo.name.lower().endswith((".jpg", ".jpeg")) else "PNG"
                img.save(buf, format=fmt, quality=85)
                self.photo.save(self.photo.name, ContentFile(buf.getvalue()), save=False)
                super().save(update_fields=["photo"])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()
