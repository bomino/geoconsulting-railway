from django.db import models


class ProjectCategory(models.TextChoices):
    ROUTES = "Routes", "Routes et voiries"
    BATIMENTS = "Bâtiments", "Bâtiments et structures"
    HYDRAULIQUE = "Hydraulique", "Hydraulique et assainissement"
    AMENAGEMENT = "Aménagement", "Aménagements urbains"
    ETUDES = "Études", "Études techniques"


class ProjectStatus(models.TextChoices):
    EN_COURS = "En cours", "En cours"
    TERMINE = "Terminé", "Terminé"
    EN_ATTENTE = "En attente", "En attente"


class ContactStatus(models.TextChoices):
    PENDING = "Pending", "En attente"
    IN_PROGRESS = "In Progress", "En cours"
    RESOLVED = "Resolved", "Résolu"


class AccessLevel(models.TextChoices):
    VIEW = "view", "Lecture"
    COMMENT = "comment", "Commentaire"
    EDIT = "edit", "Édition"


class TemplateCategory(models.TextChoices):
    QUOTE = "quote_request", "Demande de devis"
    INQUIRY = "project_inquiry", "Demande projet"
    INFO = "general_info", "Information générale"
    CUSTOM = "custom", "Personnalisé"
