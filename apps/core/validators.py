import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".gif"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024


def _validate_file(file, allowed_extensions):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _("Extension '%(ext)s' non autorisee. Extensions acceptees: %(allowed)s"),
            params={"ext": ext, "allowed": ", ".join(sorted(allowed_extensions))},
        )
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            _("Le fichier depasse la taille maximale de 50 Mo."),
        )


def validate_document_file(file):
    _validate_file(file, DOCUMENT_EXTENSIONS)


def validate_image_file(file):
    _validate_file(file, IMAGE_EXTENSIONS)
