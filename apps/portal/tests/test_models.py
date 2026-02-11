import pytest
from django.db import IntegrityError

from apps.portal.factories import ClientProjectFactory, MessageFactory, ProjectCommentFactory
from apps.portal.models import ClientProject, Message, ProjectComment


@pytest.mark.django_db
class TestClientProject:
    def test_unique_together(self):
        cp = ClientProjectFactory()
        with pytest.raises(IntegrityError):
            ClientProjectFactory(user=cp.user, project=cp.project)

    def test_str(self):
        cp = ClientProjectFactory()
        result = str(cp)
        assert cp.user.username in result
        assert cp.project.title in result

    def test_message_ordering(self):
        m1 = MessageFactory()
        m2 = MessageFactory()
        result = list(Message.objects.all())
        assert result[0] == m2

    def test_last_accessed_default_null(self):
        cp = ClientProjectFactory()
        assert cp.last_accessed is None


@pytest.mark.django_db
class TestProjectComment:
    def test_str(self):
        comment = ProjectCommentFactory()
        result = str(comment)
        assert str(comment.author) in result

    def test_ordering_ascending(self):
        c1 = ProjectCommentFactory()
        c2 = ProjectCommentFactory(project=c1.project)
        result = list(ProjectComment.objects.filter(project=c1.project))
        assert result[0] == c1
        assert result[1] == c2
