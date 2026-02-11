from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.enums import AccessLevel
from apps.portal.forms import (
    ClientDocumentUploadForm,
    ClientProfileForm,
    MessageComposeForm,
    ProjectCommentForm,
)
from apps.portal.models import ClientProject, Message, ProjectComment
from apps.projects.models import Project, ProjectDocument


def get_client_access(user, project):
    if user.is_staff:
        return None
    return ClientProject.objects.filter(user=user, project=project).first()


class ClientPortalMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request, "user") and request.user.is_authenticated:
            if not (request.user.is_staff or request.user.groups.filter(name="clients").exists()):
                raise PermissionDenied
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            if not self.request.user.is_staff:
                context["unread_count"] = Message.objects.filter(
                    to_user=self.request.user, read=False
                ).count()
        return context


class PortalDashboardView(ClientPortalMixin, ListView):
    template_name = "portal/dashboard.html"
    context_object_name = "projects"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(
            client_projects__user=self.request.user
        ).annotate(
            user_access_level=Subquery(
                ClientProject.objects.filter(
                    user=self.request.user, project=OuterRef("pk")
                ).values("access_level")[:1]
            )
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if not user.is_staff:
            accesses = ClientProject.objects.filter(user=user).select_related("project")
            badge_map = {}
            for cp in accesses:
                doc_qs = ProjectDocument.objects.filter(project=cp.project)
                if cp.last_accessed:
                    doc_qs = doc_qs.filter(created_at__gt=cp.last_accessed)
                badge_map[cp.project_id] = doc_qs.count()
            context["badge_map"] = badge_map

        project_ids = [p.pk for p in context["projects"]]
        recent_docs = ProjectDocument.objects.filter(
            project_id__in=project_ids
        ).select_related("project").order_by("-created_at")[:10]

        recent_comments = ProjectComment.objects.filter(
            project_id__in=project_ids
        ).select_related("project", "author").order_by("-created_at")[:10]

        activities = []
        for doc in recent_docs:
            activities.append({
                "type": "document",
                "text": f"Nouveau document: {doc.title}",
                "project": doc.project,
                "timestamp": doc.created_at,
            })
        for comment in recent_comments:
            activities.append({
                "type": "comment",
                "text": f"{comment.author.get_full_name() or comment.author.email}: {comment.content[:80]}",
                "project": comment.project,
                "timestamp": comment.created_at,
            })
        activities.sort(key=lambda a: a["timestamp"], reverse=True)
        context["activities"] = activities[:10]

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
        context["comments"] = self.object.comments.select_related("author").all()
        context["comment_form"] = ProjectCommentForm()
        if self.request.user.is_staff:
            context["can_comment"] = True
            context["can_edit"] = True
            context["upload_form"] = ClientDocumentUploadForm()
        else:
            access = get_object_or_404(
                ClientProject, user=self.request.user, project=self.object
            )
            context["access"] = access
            context["can_comment"] = access.access_level in (AccessLevel.COMMENT, AccessLevel.EDIT)
            context["can_edit"] = access.access_level == AccessLevel.EDIT
            if context["can_edit"]:
                context["upload_form"] = ClientDocumentUploadForm()
            access.last_accessed = timezone.now()
            access.save(update_fields=["last_accessed"])
        return context


@method_decorator(ratelimit(key="user", rate="30/h", method="POST", block=True), name="dispatch")
class ProjectCommentCreateView(ClientPortalMixin, View):
    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        if not request.user.is_staff:
            access = get_object_or_404(ClientProject, user=request.user, project=project)
            if access.access_level not in (AccessLevel.COMMENT, AccessLevel.EDIT):
                raise PermissionDenied
        form = ProjectCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            return render(request, "portal/_comment.html", {"comment": comment})
        return HttpResponse(status=422)


@method_decorator(ratelimit(key="user", rate="10/h", method="POST", block=True), name="dispatch")
class ClientDocumentUploadView(ClientPortalMixin, View):
    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        if not request.user.is_staff:
            access = get_object_or_404(ClientProject, user=request.user, project=project)
            if access.access_level != AccessLevel.EDIT:
                raise PermissionDenied
        form = ClientDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.project = project
            doc.uploaded_by = request.user
            doc.save()
            return render(request, "portal/_document_row.html", {"doc": doc})
        return HttpResponse(status=422)


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
    paginate_by = 20

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


class ClientProfileView(ClientPortalMixin, UpdateView):
    form_class = ClientProfileForm
    template_name = "portal/profile.html"
    success_url = reverse_lazy("portal_profile")

    def get_object(self, queryset=None):
        return self.request.user.profile
