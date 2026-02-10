from collections import OrderedDict

from django.http import Http404
from django.views.generic import TemplateView

from apps.articles.models import Article
from apps.core.models import FAQ, FAQCategory, SiteSetting
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
        context["featured_projects"] = (
            Project.objects.filter(published=True)[:6]
        )
        context["latest_articles"] = (
            Article.objects.filter(published=True)[:2]
        )
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
