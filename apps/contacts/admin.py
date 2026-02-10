import csv

from django.contrib import admin
from django.http import HttpResponse
from unfold.admin import ModelAdmin

from apps.contacts.models import Contact, ContactAssignment
from apps.core.enums import ContactStatus


@admin.action(description="Marquer comme lu")
def mark_read(modeladmin, request, queryset):
    queryset.update(read=True)


@admin.action(description="Marquer en cours")
def mark_in_progress(modeladmin, request, queryset):
    queryset.update(status=ContactStatus.IN_PROGRESS)


@admin.action(description="Marquer résolu")
def mark_resolved(modeladmin, request, queryset):
    queryset.update(status=ContactStatus.RESOLVED)


@admin.action(description="Archiver")
def archive_contacts(modeladmin, request, queryset):
    queryset.update(archived=True)


@admin.action(description="Exporter en CSV")
def export_contacts_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
    writer = csv.writer(response)
    writer.writerow(["Nom", "Email", "Téléphone", "Sujet", "Message", "Statut", "Date"])
    for contact in queryset:
        writer.writerow([
            contact.name,
            contact.email,
            contact.phone,
            contact.subject,
            contact.message,
            contact.status,
            contact.created_at.strftime("%Y-%m-%d %H:%M"),
        ])
    return response


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "status",
        "read",
        "archived",
        "created_at",
        "assigned_to_display",
    )
    list_filter = ("status", "read", "archived", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "created_at")
    actions = [mark_read, mark_in_progress, mark_resolved, archive_contacts, export_contacts_csv]

    @admin.display(description="Assigné à")
    def assigned_to_display(self, obj):
        assignment = obj.assignments.select_related("assigned_to").first()
        if assignment:
            return assignment.assigned_to.get_full_name() or assignment.assigned_to.username
        return "-"


@admin.register(ContactAssignment)
class ContactAssignmentAdmin(ModelAdmin):
    list_display = ("contact", "assigned_to", "assigned_by", "created_at")
    list_filter = ("assigned_to",)
    autocomplete_fields = ("contact", "assigned_to", "assigned_by")
