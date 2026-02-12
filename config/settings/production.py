import environ
from .base import *  # noqa: F401, F403

env = environ.Env()

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
RAILWAY_PUBLIC_DOMAIN = env("RAILWAY_PUBLIC_DOMAIN", default="")
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    CSRF_TRUSTED_ORIGINS = [f"https://{RAILWAY_PUBLIC_DOMAIN}"]

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

_r2_account_id = env("R2_ACCOUNT_ID", default="")
if _r2_account_id:
    _r2_origin = f"https://{_r2_account_id}.r2.cloudflarestorage.com"
    _default_storage = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": env("R2_ACCESS_KEY_ID", default=""),
            "secret_key": env("R2_SECRET_ACCESS_KEY", default=""),
            "bucket_name": env("R2_BUCKET", default="geoconsulting-files"),
            "endpoint_url": _r2_origin,
            "default_acl": "private",
            "file_overwrite": False,
            "querystring_auth": True,
            "querystring_expire": 3600,
        },
    }
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["img-src"].append(_r2_origin)
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"].append(_r2_origin)
else:
    _default_storage = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }

STORAGES = {
    "default": _default_storage,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ANYMAIL = {
    "RESEND_API_KEY": env("RESEND_API_KEY", default=""),
}
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
DEFAULT_FROM_EMAIL = env("ADMIN_EMAIL", default="info@mygeoconsulting.com")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
