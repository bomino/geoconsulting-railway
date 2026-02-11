from django.urls import path

from apps.portal.views import (
    ClientDocumentUploadView,
    ClientProfileView,
    DocumentDownloadView,
    MarkAsReadView,
    MessageComposeView,
    MessageDetailView,
    MessageListView,
    PortalDashboardView,
    PortalProjectView,
    ProjectCommentCreateView,
)

urlpatterns = [
    path("", PortalDashboardView.as_view(), name="portal_dashboard"),
    path("profil/", ClientProfileView.as_view(), name="portal_profile"),
    path("projets/<slug:slug>/", PortalProjectView.as_view(), name="portal_project"),
    path(
        "projets/<slug:slug>/telecharger/<int:doc_id>/",
        DocumentDownloadView.as_view(),
        name="portal_document_download",
    ),
    path("projets/<slug:slug>/commentaire/", ProjectCommentCreateView.as_view(), name="portal_comment_create"),
    path("projets/<slug:slug>/envoyer-document/", ClientDocumentUploadView.as_view(), name="portal_document_upload"),
    path("messages/", MessageListView.as_view(), name="portal_messages"),
    path("messages/nouveau/", MessageComposeView.as_view(), name="portal_message_compose"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="portal_message_detail"),
    path("messages/<int:pk>/lu/", MarkAsReadView.as_view(), name="portal_mark_read"),
]
