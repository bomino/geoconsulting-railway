import factory

from apps.accounts.factories import UserFactory
from apps.core.enums import AccessLevel
from apps.portal.models import ClientProject, Message, ProjectComment
from apps.projects.factories import ProjectFactory


class ClientProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientProject

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    access_level = AccessLevel.VIEW


class ProjectCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectComment

    project = factory.SubFactory(ProjectFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Sequence(lambda n: f"Commentaire de test {n}")


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)
    subject = factory.Sequence(lambda n: f"Message {n}")
    content = "Contenu du message de test."
