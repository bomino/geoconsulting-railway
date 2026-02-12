from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.core.views import HomeView
from apps.core.views_admin import admin_guide_view

urlpatterns = [
    path("healthz/", lambda r: JsonResponse({"status": "ok"})),
    path("", HomeView.as_view(), name="home"),
    path("admin/guide/", admin_guide_view, name="admin_guide"),
    path("admin/", admin.site.urls),
    path("comptes/", include("allauth.urls")),
    path("projets/", include("apps.projects.urls")),
    path("actualites/", include("apps.articles.urls")),
    path("", include("apps.core.urls")),
    path("contact/", include("apps.contacts.urls")),
    path("portail/", include("apps.portal.urls")),
    path("api/", include("apps.chatbot.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
