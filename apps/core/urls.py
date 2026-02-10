from django.urls import path

from apps.core.views import AboutView, FAQView, ServiceDetailView, ServicesView

urlpatterns = [
    path("a-propos/", AboutView.as_view(), name="about"),
    path("services/", ServicesView.as_view(), name="services"),
    path("services/<slug:slug>/", ServiceDetailView.as_view(), name="service_detail"),
    path("faq/", FAQView.as_view(), name="faq"),
]
