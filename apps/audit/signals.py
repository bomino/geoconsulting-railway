from django.db.models.signals import post_delete, post_save

from apps.audit.services import log_audit_event


def _get_user(instance):
    for attr in ("updated_by", "created_by", "user", "from_user"):
        user = getattr(instance, attr, None)
        if user is not None:
            return user
    return None


def _on_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    log_audit_event(
        user=_get_user(instance),
        action=action,
        entity_type=sender.__name__,
        entity_id=instance.pk,
    )


def _on_delete(sender, instance, **kwargs):
    log_audit_event(
        user=_get_user(instance),
        action="deleted",
        entity_type=sender.__name__,
        entity_id=instance.pk,
    )


def register_audit_signals():
    from apps.articles.models import Article
    from apps.contacts.models import Contact
    from apps.crm.models import AssignmentRule, EmailTemplate
    from apps.portal.models import ClientProject, Message
    from apps.projects.models import Project

    models = [Project, Article, Contact, ClientProject, Message, EmailTemplate, AssignmentRule]
    for model in models:
        post_save.connect(_on_save, sender=model, dispatch_uid=f"audit_save_{model.__name__}")
        post_delete.connect(_on_delete, sender=model, dispatch_uid=f"audit_delete_{model.__name__}")
