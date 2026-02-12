from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, StackedInline

from apps.accounts.models import Profile, User


class ProfileInline(StackedInline):
    model = Profile
    can_delete = False
    fields = ("phone", "avatar")
    extra = 0


@admin.action(description="Assigner le rôle client")
def set_as_client(modeladmin, request, queryset):
    from django.contrib.auth.models import Group

    group, _ = Group.objects.get_or_create(name="clients")
    admins_group, _ = Group.objects.get_or_create(name="admins")
    for user in queryset:
        user.groups.add(group)
        user.groups.remove(admins_group)
        user.is_staff = False
        user.save(update_fields=["is_staff"])


@admin.action(description="Assigner le rôle admin")
def set_as_admin(modeladmin, request, queryset):
    from django.contrib.auth.models import Group

    group, _ = Group.objects.get_or_create(name="admins")
    clients_group, _ = Group.objects.get_or_create(name="clients")
    for user in queryset:
        user.groups.add(group)
        user.groups.remove(clients_group)
        user.is_staff = True
        user.save(update_fields=["is_staff"])


@admin.action(description="Assigner le rôle invité")
def set_as_guest(modeladmin, request, queryset):
    from django.contrib.auth.models import Group

    for user in queryset:
        user.groups.clear()
        user.is_staff = False
        user.save(update_fields=["is_staff"])


@admin.action(description="Suppression douce des utilisateurs sélectionnés")
def soft_delete_selected(modeladmin, request, queryset):
    for user in queryset:
        user.soft_delete()


@admin.action(description="Restaurer les utilisateurs sélectionnés")
def restore_selected(modeladmin, request, queryset):
    for user in queryset:
        user.restore()


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informations personnelles"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Dates"), {"fields": ("last_login", "date_joined")}),
        (_("Suppression douce"), {"fields": ("is_deleted", "deleted_at")}),
    )
    readonly_fields = ("is_deleted", "deleted_at", "last_login", "date_joined")
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role_display",
        "is_deleted",
        "date_joined",
        "last_login",
    )
    list_filter = ("groups", "is_staff", "is_active", "is_deleted")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    inlines = [ProfileInline]
    actions = [set_as_client, set_as_admin, set_as_guest, soft_delete_selected, restore_selected]

    @admin.display(description="Rôle")
    def role_display(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.role
        if obj.is_staff:
            return "admin"
        return "guest"

    def get_queryset(self, request):
        return User.all_objects.all()

    def has_delete_permission(self, request, obj=None):
        return False
