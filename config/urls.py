from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

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
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

if not hasattr(settings, "STORAGES") or settings.STORAGES.get("default", {}).get(
    "BACKEND"
) == "django.core.files.storage.FileSystemStorage":
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            static_serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
