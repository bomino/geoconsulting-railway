import factory
from django.utils.text import slugify

from apps.accounts.factories import UserFactory
from apps.core.models import FAQ, Department, Division, FAQCategory, SiteSetting, TeamMember


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    question = factory.Sequence(lambda n: f"Question {n}?")
    answer = "Reponse de test."
    category = FAQCategory.GENERAL
    order = factory.Sequence(lambda n: n)
    published = True
    created_by = factory.SubFactory(UserFactory)


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Département {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    order = factory.Sequence(lambda n: n)
    published = True


class DivisionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Division

    name = factory.Sequence(lambda n: f"Division {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    department = factory.SubFactory(DepartmentFactory)
    order = factory.Sequence(lambda n: n)
    published = True


class TeamMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMember

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "Ingenieur"
    department = factory.SubFactory(DepartmentFactory)
    order = factory.Sequence(lambda n: n)
    published = True


class SiteSettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiteSetting

    key = factory.Sequence(lambda n: f"setting_{n}")
    value = "test value"
