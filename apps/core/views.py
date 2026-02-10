from collections import OrderedDict

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.http import Http404
from django.views.generic import ListView, TemplateView

from apps.articles.models import Article
from apps.core.enums import Department
from apps.core.models import FAQ, FAQCategory, SiteSetting, TeamMember
from apps.projects.models import Project

SERVICES = [
    {
        "slug": "etudes-techniques",
        "name": "Études Techniques",
        "short": "Études de faisabilité, calculs de structures, études d'impact environnemental et social.",
        "items": [
            "Études de faisabilité technique des infrastructures routières et de voiries",
            "Calculs de structures des ouvrages en béton et métallique (bâtiments, dalots, ponts\u2026)",
            "Études techniques de routes en terre",
            "Recommandations en matière de choix stratégiques des projets d'infrastructures",
            "Études portuaires et aéroportuaires",
            "Études d'infrastructures hydrauliques urbaines et villageoises (Mini AEP, forage, puits)",
            "Études d'impact environnemental et social",
            "Études d'aménagements hydro-agricoles",
            "Programmation des travaux neufs de bitumage et de renforcement (modèle HDM)",
        ],
    },
    {
        "slug": "suivi-controle",
        "name": "Suivi-Contrôle et Coordination",
        "short": "Suivi et contrôle des travaux d'infrastructures routières, bâtiments et hydraulique.",
        "items": [
            "Suivi-Contrôle des travaux d'infrastructures routières",
            "Suivi-Contrôle et coordination des travaux de construction de bâtiments",
            "Suivi-Contrôle hydraulique (Mini AEP, Puits, Forage)",
        ],
    },
    {
        "slug": "essai-laboratoire",
        "name": "Essai Laboratoire",
        "short": "Géotechnique routière, études de fondation, essais bitume, béton et hydraulique.",
        "items": [
            "Géotechnique routière (sondage, CBR, Proctor, granulométrie, Compacité, Los Angeles, MDE)",
            "Étude de fondation bâtiment (Sondage, Pénétromètre léger, Proctor, Compacité)",
            "Étude Bitume (bille anneau, pénétrabilité)",
            "Étude béton (formulation de béton, essai de compression)",
            "Hydraulique (essai de pression)",
        ],
    },
]

SERVICES_BY_SLUG = {s["slug"]: s for s in SERVICES}


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_projects"] = Project.objects.filter(published=True)[:6]
        context["latest_articles"] = Article.objects.filter(published=True)[:3]
        context["project_count"] = Project.objects.filter(published=True).count()
        context["services"] = SERVICES
        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_qs = SiteSetting.objects.filter(
            key__in=["organigramme_image", "politique_qualite_image"]
        )
        site_settings = {s.key: s for s in settings_qs}
        context["organigramme"] = site_settings.get("organigramme_image")
        context["politique_qualite"] = site_settings.get("politique_qualite_image")

        team_members = TeamMember.objects.filter(published=True)
        context["direction"] = [m for m in team_members if m.department == Department.DIRECTION]
        departments = OrderedDict()
        for member in team_members:
            if member.department == Department.DIRECTION:
                continue
            label = Department(member.department).label
            departments.setdefault(label, []).append(member)
        context["departments"] = departments

        return context


class ServicesView(TemplateView):
    template_name = "pages/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = SERVICES
        return context


class ServiceDetailView(TemplateView):
    template_name = "pages/service_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["slug"]
        service = SERVICES_BY_SLUG.get(slug)
        if service is None:
            raise Http404
        context["service"] = service
        return context


class FAQView(TemplateView):
    template_name = "pages/faq.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faqs = FAQ.objects.filter(published=True).order_by("category", "order")
        grouped = OrderedDict()
        for faq in faqs:
            label = FAQCategory(faq.category).label
            grouped.setdefault(label, []).append(faq)
        context["faq_groups"] = grouped
        return context


class SearchView(ListView):
    template_name = "pages/search.html"
    context_object_name = "results"

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()[:200]
        context["query"] = query

        if query:
            search_query = SearchQuery(query, config="french")

            projects = (
                Project.objects.filter(published=True, search_vector=search_query)
                .annotate(rank=SearchRank("search_vector", search_query))
                .order_by("-rank")[:5]
            )
            articles = (
                Article.objects.filter(published=True, search_vector=search_query)
                .annotate(rank=SearchRank("search_vector", search_query))
                .order_by("-rank")[:5]
            )

            query_lower = query.lower()
            matched_services = [
                s for s in SERVICES
                if query_lower in s["name"].lower()
                or any(query_lower in item.lower() for item in s["items"])
            ]

            context["projects"] = projects
            context["articles"] = articles
            context["services"] = matched_services

        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["partials/_search_results.html"]
        return [self.template_name]
