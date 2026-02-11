import pytest
from django.contrib.auth.models import Group
from django.test import Client

from apps.accounts.factories import StaffUserFactory, UserFactory
from apps.core.enums import AccessLevel, ProjectStatus
from apps.portal.factories import ClientProjectFactory, MessageFactory, ProjectCommentFactory
from apps.portal.models import ClientProject, Message, ProjectComment
from apps.projects.factories import ProjectDocumentFactory, ProjectFactory


@pytest.fixture
def client_group(db):
    group, _ = Group.objects.get_or_create(name="clients")
    return group


def make_client_user(client_group):
    user = UserFactory()
    user.groups.add(client_group)
    return user


@pytest.mark.django_db
class TestPortalDashboard:
    def test_anon_redirects(self):
        c = Client()
        response = c.get("/portail/")
        assert response.status_code == 302

    def test_regular_user_403(self):
        user = UserFactory()
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        assert response.status_code == 403

    def test_client_200(self, client_group):
        user = make_client_user(client_group)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        assert response.status_code == 200

    def test_staff_sees_all(self):
        staff = StaffUserFactory()
        ProjectFactory()
        ProjectFactory()
        c = Client()
        c.force_login(staff)
        response = c.get("/portail/")
        assert response.status_code == 200
        assert len(response.context["projects"]) == 2

    def test_client_sees_only_assigned(self, client_group):
        user = make_client_user(client_group)
        p1 = ProjectFactory()
        ProjectFactory()
        ClientProjectFactory(user=user, project=p1)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        projects = list(response.context["projects"])
        assert len(projects) == 1
        assert projects[0] == p1

    def test_badge_map_in_context(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p)
        ProjectDocumentFactory(project=p)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        badge_map = response.context["badge_map"]
        assert p.pk in badge_map
        assert badge_map[p.pk] >= 1

    def test_activities_in_context(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p)
        ProjectDocumentFactory(project=p)
        ProjectCommentFactory(project=p)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        activities = response.context["activities"]
        assert len(activities) == 2

    def test_unread_count_in_context(self, client_group):
        user = make_client_user(client_group)
        MessageFactory(to_user=user, read=False)
        MessageFactory(to_user=user, read=True)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        assert response.context["unread_count"] == 1

    def test_status_badge_renders(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory(status=ProjectStatus.TERMINE)
        ClientProjectFactory(user=user, project=p)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/")
        content = response.content.decode()
        assert "bg-secondary-100" in content


@pytest.mark.django_db
class TestPortalProjectDetail:
    def test_client_no_access_403(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory(slug="restricted")
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.status_code == 403

    def test_client_with_access_200(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory(slug="accessible")
        ClientProjectFactory(user=user, project=p)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.status_code == 200

    def test_view_access_cannot_comment(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.VIEW)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.context["can_comment"] is False
        assert response.context["can_edit"] is False

    def test_comment_access_can_comment(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.COMMENT)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.context["can_comment"] is True
        assert response.context["can_edit"] is False

    def test_edit_access_can_edit(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.EDIT)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.context["can_comment"] is True
        assert response.context["can_edit"] is True

    def test_staff_has_full_access(self):
        staff = StaffUserFactory()
        p = ProjectFactory()
        c = Client()
        c.force_login(staff)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert response.context["can_comment"] is True
        assert response.context["can_edit"] is True

    def test_updates_last_accessed(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        cp = ClientProjectFactory(user=user, project=p)
        assert cp.last_accessed is None
        c = Client()
        c.force_login(user)
        c.get(f"/portail/projets/{p.slug}/")
        cp.refresh_from_db()
        assert cp.last_accessed is not None

    def test_comments_in_context(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p)
        ProjectCommentFactory(project=p)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert len(response.context["comments"]) == 1

    def test_comment_access_no_upload_form(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.COMMENT)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert "upload_form" not in response.context

    def test_view_access_no_upload_form(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.VIEW)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{p.slug}/")
        assert "upload_form" not in response.context


@pytest.mark.django_db
class TestProjectCommentCreate:
    def test_view_access_cannot_comment(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.VIEW)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/projets/{p.slug}/commentaire/", {"content": "Test"})
        assert response.status_code == 403

    def test_comment_access_can_post(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.COMMENT)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/projets/{p.slug}/commentaire/", {"content": "Mon commentaire"})
        assert response.status_code == 200
        assert ProjectComment.objects.filter(project=p, author=user).exists()

    def test_staff_can_comment(self):
        staff = StaffUserFactory()
        p = ProjectFactory()
        c = Client()
        c.force_login(staff)
        response = c.post(f"/portail/projets/{p.slug}/commentaire/", {"content": "Staff comment"})
        assert response.status_code == 200

    def test_empty_content_rejected(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.COMMENT)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/projets/{p.slug}/commentaire/", {"content": ""})
        assert response.status_code == 422


@pytest.mark.django_db
class TestClientDocumentUpload:
    def test_view_access_cannot_upload(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.VIEW)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/projets/{p.slug}/envoyer-document/", {})
        assert response.status_code == 403

    def test_comment_access_cannot_upload(self, client_group):
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.COMMENT)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/projets/{p.slug}/envoyer-document/", {})
        assert response.status_code == 403

    def test_edit_access_can_upload(self, client_group):
        from django.core.files.uploadedfile import SimpleUploadedFile
        user = make_client_user(client_group)
        p = ProjectFactory()
        ClientProjectFactory(user=user, project=p, access_level=AccessLevel.EDIT)
        c = Client()
        c.force_login(user)
        test_file = SimpleUploadedFile("test.pdf", b"%PDF-1.4 fake content", content_type="application/pdf")
        response = c.post(
            f"/portail/projets/{p.slug}/envoyer-document/",
            {"title": "Mon rapport", "file": test_file, "category": "Rapport"},
        )
        assert response.status_code == 200
        from apps.projects.models import ProjectDocument
        assert ProjectDocument.objects.filter(project=p, uploaded_by=user).exists()


@pytest.mark.django_db
class TestPortalMessages:
    def test_message_list_scoped_to_user(self, client_group):
        user = make_client_user(client_group)
        other = UserFactory()
        msg_to_user = MessageFactory(to_user=user, from_user=other)
        msg_to_other = MessageFactory(to_user=other, from_user=user)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/messages/")
        messages = list(response.context["messages"])
        assert msg_to_user in messages
        assert msg_to_other not in messages

    def test_message_detail_auto_marks_read(self, client_group):
        user = make_client_user(client_group)
        msg = MessageFactory(to_user=user, read=False)
        c = Client()
        c.force_login(user)
        c.get(f"/portail/messages/{msg.pk}/")
        msg.refresh_from_db()
        assert msg.read is True

    def test_compose_sets_from_user(self, client_group):
        user = make_client_user(client_group)
        staff = StaffUserFactory()
        c = Client()
        c.force_login(user)
        response = c.post(
            "/portail/messages/nouveau/",
            {"to_user": staff.pk, "subject": "Test", "content": "Bonjour"},
        )
        assert response.status_code == 302
        msg = Message.objects.filter(from_user=user).first()
        assert msg is not None
        assert msg.to_user == staff

    def test_mark_as_read_get_not_allowed(self, client_group):
        user = make_client_user(client_group)
        msg = MessageFactory(to_user=user, read=False)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/messages/{msg.pk}/lu/")
        assert response.status_code == 405

    def test_mark_as_read_post_204(self, client_group):
        user = make_client_user(client_group)
        msg = MessageFactory(to_user=user, read=False)
        c = Client()
        c.force_login(user)
        response = c.post(f"/portail/messages/{msg.pk}/lu/")
        assert response.status_code == 204
        msg.refresh_from_db()
        assert msg.read is True

    def test_pagination_20(self, client_group):
        user = make_client_user(client_group)
        for _ in range(25):
            MessageFactory(to_user=user)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/messages/")
        assert response.context["is_paginated"] is True
        assert len(response.context["messages"]) == 20


@pytest.mark.django_db
class TestDocumentDownload:
    def test_client_no_access_403(self, client_group):
        user = make_client_user(client_group)
        doc = ProjectDocumentFactory()
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{doc.project.slug}/telecharger/{doc.pk}/")
        assert response.status_code == 403

    def test_staff_can_download(self):
        staff = StaffUserFactory()
        doc = ProjectDocumentFactory()
        c = Client()
        c.force_login(staff)
        response = c.get(f"/portail/projets/{doc.project.slug}/telecharger/{doc.pk}/")
        assert response.status_code == 302

    def test_client_with_access_can_download(self, client_group):
        user = make_client_user(client_group)
        doc = ProjectDocumentFactory()
        ClientProjectFactory(user=user, project=doc.project)
        c = Client()
        c.force_login(user)
        response = c.get(f"/portail/projets/{doc.project.slug}/telecharger/{doc.pk}/")
        assert response.status_code == 302


@pytest.mark.django_db
class TestClientProfile:
    def test_profile_200(self, client_group):
        user = make_client_user(client_group)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/profil/")
        assert response.status_code == 200

    def test_profile_update(self, client_group):
        user = make_client_user(client_group)
        c = Client()
        c.force_login(user)
        response = c.post(
            "/portail/profil/",
            {"first_name": "Jean", "last_name": "Dupont", "phone": "+227 12 34"},
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == "Jean"
        assert user.last_name == "Dupont"

    def test_unread_count_on_profile(self, client_group):
        user = make_client_user(client_group)
        MessageFactory(to_user=user, read=False)
        c = Client()
        c.force_login(user)
        response = c.get("/portail/profil/")
        assert response.context["unread_count"] == 1
