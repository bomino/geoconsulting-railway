from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from apps.portal.forms import MessageComposeForm
from apps.portal.models import ClientProject, Message
from apps.projects.models import Project, ProjectDocument


class ClientPortalMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request, "user") and request.user.is_authenticated:
            if not (request.user.is_staff or request.user.groups.filter(name="clients").exists()):
                raise PermissionDenied
        return response


class PortalDashboardView(ClientPortalMixin, ListView):
    template_name = "portal/dashboard.html"
    context_object_name = "projects"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(
            client_projects__user=self.request.user
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_staff:
            context["unread_count"] = Message.objects.filter(
                to_user=self.request.user, read=False
            ).count()
        return context


class PortalProjectView(ClientPortalMixin, DetailView):
    model = Project
    template_name = "portal/project_detail.html"
    context_object_name = "project"

    def get_object(self, queryset=None):
        project = super().get_object(queryset)
        if not self.request.user.is_staff:
            if not ClientProject.objects.filter(
                user=self.request.user, project=project
            ).exists():
                raise PermissionDenied
        return project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.object.documents.all()
        if not self.request.user.is_staff:
            context["access"] = get_object_or_404(
                ClientProject, user=self.request.user, project=self.object
            )
        return context


class DocumentDownloadView(ClientPortalMixin, View):
    def get(self, request, slug, doc_id):
        document = get_object_or_404(ProjectDocument, pk=doc_id, project__slug=slug)
        if not request.user.is_staff:
            if not ClientProject.objects.filter(
                user=request.user, project=document.project
            ).exists():
                raise PermissionDenied
        url = default_storage.url(document.file.name)
        return redirect(url)


class MessageListView(ClientPortalMixin, ListView):
    template_name = "portal/messages.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(
            to_user=self.request.user
        ).select_related("from_user")


class MessageComposeView(ClientPortalMixin, CreateView):
    model = Message
    form_class = MessageComposeForm
    template_name = "portal/message_compose.html"
    success_url = reverse_lazy("portal_messages")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["sender"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        return super().form_valid(form)


class MessageDetailView(ClientPortalMixin, DetailView):
    model = Message
    template_name = "portal/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        return Message.objects.filter(
            Q(to_user=self.request.user) | Q(from_user=self.request.user)
        ).select_related("from_user", "to_user")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.to_user == self.request.user and not obj.read:
            obj.read = True
            obj.save(update_fields=["read"])
        return obj


class MarkAsReadView(ClientPortalMixin, View):
    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk, to_user=request.user)
        message.read = True
        message.save(update_fields=["read"])
        return HttpResponse(status=204)
