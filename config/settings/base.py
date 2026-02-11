import environ
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

AUTH_USER_MODEL = "accounts.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "anymail",
    "storages",
    "csp",
    "apps.core",
    "apps.accounts",
    "apps.projects",
    "apps.articles",
    "apps.contacts",
    "apps.portal",
    "apps.crm",
    "apps.chatbot",
    "apps.audit",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "apps.audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.company_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://geo:geo@localhost:5432/geoconsulting"),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="info@mygeoconsulting.com")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Niamey"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_RATE_LIMITS = {
    "login": "5/m/ip",
    "login_failed": "5/m/ip,3/5m/key",
    "signup": "5/m/ip",
    "password_reset": "5/m/ip",
}

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "cdn.jsdelivr.net"],
        "style-src": ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
        "img-src": ["'self'", "data:", "blob:"],
        "font-src": ["'self'", "fonts.gstatic.com"],
        "connect-src": ["'self'"],
        "frame-src": ["'none'"],
        "object-src": ["'none'"],
        "form-action": ["'self'"],
        "base-uri": ["'self'"],
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

UNFOLD = {
    "SITE_TITLE": "GeoConsulting Admin",
    "SITE_HEADER": "GeoConsulting",
    "SITE_SUBHEADER": "Administration",
    "SITE_URL": "/",
    "SITE_SYMBOL": "engineering",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "primary": {
            "50": "#E8EEF6",
            "100": "#D1DDED",
            "200": "#A3BBD8",
            "300": "#7599C4",
            "400": "#4777AF",
            "500": "#2A5298",
            "600": "#22447D",
            "700": "#1B3A6B",
            "800": "#142D54",
            "900": "#0D1F3D",
            "950": "#081428",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Gestion du site"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Tableau de bord"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Utilisateurs"),
                        "icon": "people",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": _("Équipe"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:core_teammember_changelist"),
                    },
                    {
                        "title": _("Départements"),
                        "icon": "corporate_fare",
                        "link": reverse_lazy("admin:core_department_changelist"),
                    },
                    {
                        "title": _("Divisions"),
                        "icon": "account_tree",
                        "link": reverse_lazy("admin:core_division_changelist"),
                    },
                    {
                        "title": _("Paramètres du site"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesetting_changelist"),
                    },
                    {
                        "title": _("Guide d'administration"),
                        "icon": "menu_book",
                        "link": lambda request: "/admin/guide/",
                    },
                ],
            },
            {
                "title": _("Contenu"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Projets"),
                        "icon": "construction",
                        "link": reverse_lazy("admin:projects_project_changelist"),
                    },
                    {
                        "title": _("Articles"),
                        "icon": "article",
                        "link": reverse_lazy("admin:articles_article_changelist"),
                    },
                    {
                        "title": _("FAQ"),
                        "icon": "help",
                        "link": reverse_lazy("admin:core_faq_changelist"),
                    },
                ],
            },
            {
                "title": _("Relations clients"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Contacts"),
                        "icon": "mail",
                        "link": reverse_lazy("admin:contacts_contact_changelist"),
                    },
                    {
                        "title": _("Portail client"),
                        "icon": "account_circle",
                        "link": reverse_lazy("admin:portal_clientproject_changelist"),
                    },
                    {
                        "title": _("Modèles email"),
                        "icon": "drafts",
                        "link": reverse_lazy("admin:crm_emailtemplate_changelist"),
                    },
                    {
                        "title": _("Règles d'attribution"),
                        "icon": "assignment",
                        "link": reverse_lazy("admin:crm_assignmentrule_changelist"),
                    },
                ],
            },
            {
                "title": _("Système"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Journal d'audit"),
                        "icon": "security",
                        "link": reverse_lazy("admin:audit_auditlog_changelist"),
                    },
                ],
            },
        ],
    },
}
