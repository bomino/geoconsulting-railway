from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from apps.core.models import SoftDeleteManager, SoftDeleteMixin, TimestampMixin
from apps.core.validators import validate_image_file


class SoftDeleteUserManager(SoftDeleteManager, UserManager):
    pass


class User(SoftDeleteMixin, AbstractUser):
    objects = SoftDeleteUserManager()
    all_objects = UserManager()

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def delete(self, *args, **kwargs):
        self.soft_delete()

    def hard_delete(self):
        super().delete()


class Profile(TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, validators=[validate_image_file])

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    @property
    def role(self):
        if self.user.is_staff:
            return "admin"
        if self.user.groups.filter(name="clients").exists():
            return "client"
        return "guest"
