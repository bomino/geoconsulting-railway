from unittest.mock import patch

import pytest

from apps.core.enums import ProjectStatus
from apps.portal.factories import ClientProjectFactory
from apps.projects.factories import ProjectDocumentFactory, ProjectFactory


@pytest.mark.django_db
class TestClientProjectSignals:
    @patch("apps.core.services.send_notification")
    def test_created_sends_notification(self, mock_notify):
        ClientProjectFactory()
        mock_notify.assert_called_once()

    @patch("apps.core.services.send_notification")
    def test_update_no_notification(self, mock_notify):
        cp = ClientProjectFactory()
        mock_notify.reset_mock()
        cp.access_level = "edit"
        cp.save()
        mock_notify.assert_not_called()


@pytest.mark.django_db
class TestDocumentUploadSignals:
    @patch("apps.core.services.send_notification")
    def test_upload_notifies_clients(self, mock_notify):
        project = ProjectFactory()
        ClientProjectFactory(project=project)
        ClientProjectFactory(project=project)
        mock_notify.reset_mock()
        ProjectDocumentFactory(project=project)
        mock_notify.assert_called_once()
        recipient_list = mock_notify.call_args[1].get("recipient_list", [])
        assert len(recipient_list) == 2

    @patch("apps.core.services.send_notification")
    def test_no_clients_no_notification(self, mock_notify):
        project = ProjectFactory()
        mock_notify.reset_mock()
        ProjectDocumentFactory(project=project)
        mock_notify.assert_not_called()


@pytest.mark.django_db
class TestStatusChangeSignals:
    @patch("apps.core.services.send_notification")
    def test_status_change_notifies_clients(self, mock_notify):
        project = ProjectFactory(status=ProjectStatus.EN_COURS)
        ClientProjectFactory(project=project)
        mock_notify.reset_mock()
        project.status = ProjectStatus.TERMINE
        project.save()
        mock_notify.assert_called_once()
        call_kwargs = mock_notify.call_args[1]
        assert "status_changed" in call_kwargs["template_name"]

    @patch("apps.core.services.send_notification")
    def test_no_status_change_no_notification(self, mock_notify):
        project = ProjectFactory(status=ProjectStatus.EN_COURS)
        ClientProjectFactory(project=project)
        mock_notify.reset_mock()
        project.description = "Updated"
        project.save()
        mock_notify.assert_not_called()

    @patch("apps.core.services.send_notification")
    def test_new_project_no_notification(self, mock_notify):
        mock_notify.reset_mock()
        ProjectFactory()
        mock_notify.assert_not_called()

    @patch("apps.core.services.send_notification")
    def test_no_clients_no_notification(self, mock_notify):
        project = ProjectFactory(status=ProjectStatus.EN_COURS)
        mock_notify.reset_mock()
        project.status = ProjectStatus.TERMINE
        project.save()
        mock_notify.assert_not_called()
