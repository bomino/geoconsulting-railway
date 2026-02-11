from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.portal.models import ClientProject
from apps.projects.models import Project, ProjectDocument


@receiver(post_save, sender=ClientProject)
def on_client_project_assigned(sender, instance, created, **kwargs):
    if created:
        from apps.core.services import send_notification

        send_notification(
            subject=f"Accès au projet: {instance.project.title}",
            template_name="project_assigned",
            context={
                "client_project": instance,
                "portal_url": "/portail/",
            },
            recipient_list=[instance.user.email],
        )


@receiver(post_save, sender=ProjectDocument)
def on_document_uploaded(sender, instance, created, **kwargs):
    if created:
        from apps.core.services import send_notification

        recipient_emails = list(
            ClientProject.objects.filter(
                project=instance.project
            ).exclude(
                user__email=""
            ).values_list("user__email", flat=True)
        )

        if not recipient_emails:
            return

        send_notification(
            subject=f"Nouveau document: {instance.title}",
            template_name="document_uploaded",
            context={
                "document": instance,
                "project": instance.project,
            },
            recipient_list=recipient_emails,
        )


@receiver(pre_save, sender=Project)
def on_project_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = Project.objects.values_list("status", flat=True).get(pk=instance.pk)
        except Project.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Project)
def on_project_status_changed(sender, instance, created, **kwargs):
    if created:
        return
    old_status = getattr(instance, "_old_status", None)
    if old_status is None or old_status == instance.status:
        return

    from apps.core.services import send_notification

    recipient_emails = list(
        ClientProject.objects.filter(
            project=instance
        ).exclude(
            user__email=""
        ).values_list("user__email", flat=True)
    )

    if not recipient_emails:
        return

    send_notification(
        subject=f"Projet mis a jour: {instance.title}",
        template_name="status_changed",
        context={
            "project": instance,
            "old_status": old_status,
            "new_status": instance.get_status_display(),
            "portal_url": "/portail/",
        },
        recipient_list=recipient_emails,
    )
