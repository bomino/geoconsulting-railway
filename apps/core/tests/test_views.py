import pytest
from django.test import Client

from apps.accounts.factories import UserFactory
from apps.core.factories import (
    DepartmentFactory,
    FAQFactory,
    SiteSettingFactory,
    TeamMemberFactory,
)
from apps.core.models import FAQCategory
from apps.projects.factories import ProjectFactory


@pytest.mark.django_db
class TestHomeView:
    def setup_method(self):
        self.client = Client()

    def test_home_200(self):
        response = self.client.get("/")
        assert response.status_code == 200

    def test_home_context_featured_projects(self):
        ProjectFactory.create_batch(8)
        response = self.client.get("/")
        assert len(response.context["featured_projects"]) == 6

    def test_home_context_services(self):
        response = self.client.get("/")
        assert len(response.context["services"]) == 3

    def test_home_context_project_count(self):
        ProjectFactory.create_batch(3)
        response = self.client.get("/")
        assert response.context["project_count"] == 3


@pytest.mark.django_db
class TestAboutView:
    def setup_method(self):
        self.client = Client()

    def test_about_200(self):
        response = self.client.get("/a-propos/")
        assert response.status_code == 200

    def test_about_context_site_settings(self):
        SiteSettingFactory(key="organigramme_image")
        SiteSettingFactory(key="politique_qualite_image")
        response = self.client.get("/a-propos/")
        assert response.context["organigramme"] is not None
        assert response.context["politique_qualite"] is not None

    def test_about_context_team_members(self):
        from apps.core.models import Department, Division

        Division.objects.all().delete()
        Department.objects.all().delete()
        direction = DepartmentFactory(name="Direction", is_direction=True, order=0)
        DepartmentFactory(name="Recherche", order=1)
        DepartmentFactory(name="Administratif", order=2)
        etudes = DepartmentFactory(name="Études", order=3)
        labo = DepartmentFactory(name="Laboratoire", order=4)
        TeamMemberFactory(department=direction)
        TeamMemberFactory(department=etudes)
        TeamMemberFactory(department=labo)
        response = self.client.get("/a-propos/")
        assert len(response.context["direction"]) == 1
        org_chart = response.context["org_chart"]
        assert len(org_chart) == 4
        dept_labels = [d["label"] for d in org_chart]
        assert "Laboratoire" in dept_labels


@pytest.mark.django_db
class TestServicesView:
    def setup_method(self):
        self.client = Client()

    def test_services_200(self):
        response = self.client.get("/services/")
        assert response.status_code == 200

    def test_services_context(self):
        response = self.client.get("/services/")
        assert len(response.context["services"]) == 3


@pytest.mark.django_db
class TestServiceDetailView:
    def setup_method(self):
        self.client = Client()

    def test_valid_slug_200(self):
        response = self.client.get("/services/etudes-techniques/")
        assert response.status_code == 200
        assert response.context["service"]["name"] == "Études Techniques"

    def test_invalid_slug_404(self):
        response = self.client.get("/services/nonexistent/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestFAQView:
    def setup_method(self):
        self.client = Client()

    def test_faq_200(self):
        response = self.client.get("/faq/")
        assert response.status_code == 200

    def test_faq_groups_by_category(self):
        user = UserFactory()
        FAQFactory(category=FAQCategory.GENERAL, created_by=user)
        FAQFactory(category=FAQCategory.SERVICES, created_by=user)
        response = self.client.get("/faq/")
        groups = response.context["faq_groups"]
        assert len(groups) >= 2


@pytest.mark.django_db
class TestSearchView:
    def setup_method(self):
        self.client = Client()

    def test_search_empty_query_200(self):
        response = self.client.get("/recherche/")
        assert response.status_code == 200
        assert response.context["query"] == ""

    def test_search_with_query_returns_context(self):
        response = self.client.get("/recherche/?q=route")
        assert response.status_code == 200
        assert response.context["query"] == "route"
        assert "services" in response.context

    def test_search_service_matching(self):
        response = self.client.get("/recherche/?q=laboratoire")
        assert response.status_code == 200
        matched = response.context.get("services", [])
        slugs = [s["slug"] for s in matched]
        assert "essai-laboratoire" in slugs

    def test_search_htmx_returns_partial(self):
        response = self.client.get("/recherche/?q=test", HTTP_HX_REQUEST="true")
        assert response.status_code == 200
