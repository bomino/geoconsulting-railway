from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image

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


class Department(TimestampMixin):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_direction = models.BooleanField(
        default=False,
        help_text="Affiché en haut de l'organigramme, pas dans la grille",
    )
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Département"
        verbose_name_plural = "Départements"

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_direction:
            qs = Department.objects.filter(is_direction=True).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"is_direction": "Un seul département peut être marqué comme direction."}
                )


class Division(TimestampMixin):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="divisions"
    )
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["department", "order", "name"]
        unique_together = [("department", "name")]
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

    def __str__(self):
        return self.name


class TeamMember(TimestampMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="members",
    )
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, related_name="members",
        null=True, blank=True,
    )
    photo = models.ImageField(upload_to="team/", blank=True, validators=[validate_image_file])
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["department__order", "division__order", "order", "last_name"]
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"

    def clean(self):
        if self.division and self.division.department_id != self.department_id:
            raise ValidationError(
                {"division": "La division doit appartenir au département sélectionné."}
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            with self.photo.storage.open(self.photo.name) as f:
                img = Image.open(f)
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
