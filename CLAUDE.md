# GeoConsulting Django Project

## Stack

- Django 5.1 + PostgreSQL 16 + Tailwind 4 + HTMX 2 + Alpine.js 3
- Auth: django-allauth (email-based, at `/comptes/`)
- Admin: django-unfold
- Storage: Cloudflare R2 via django-storages
- Email: Resend via django-anymail
- AI: OpenAI streaming (SSE) with circuit breaker
- Security: django-csp 4.0, Argon2, django-ratelimit 4.x

## Project Layout

```
config/settings/{base,development,production}.py  # Split settings
apps/{accounts,core,projects,articles,contacts,portal,crm,chatbot,audit}/
templates/{pages,partials,allauth,admin}/
static/css/main.css  # Tailwind source (build: npm run build:css)
requirements/{base,dev,prod}.txt
```

## Key Conventions

### Settings
- `AUTH_USER_MODEL = "accounts.User"` (custom user, email-based login)
- env vars via `django-environ` from `.env`
- `LANGUAGE_CODE = "fr-fr"`, `TIME_ZONE = "Africa/Niamey"`

### Models
- All models use `TimestampMixin` (created_at/updated_at) from `apps.core.models`
- Enums in `apps/core/enums.py` (ProjectCategory, ProjectStatus, Department, FAQCategory)
- Validators in `apps/core/validators.py` (50MB file limit)
- `ImageField.max_length=100` default includes `upload_to` prefix path

### URLs
- `/` home, `/projets/` projects, `/actualites/` articles
- `/a-propos/` about, `/services/` services, `/faq/` FAQ, `/contact/` contact
- `/portail/` client portal, `/api/` chatbot, `/comptes/` auth, `/admin/` admin

### Templates
- Base: `templates/base.html` (Tailwind + HTMX + Alpine CDN)
- Pages: `templates/pages/{home,about,services,service_detail,contact,faq,search}.html`
- HTMX partials: `templates/partials/_*.html`

### Admin
- django-unfold with custom sidebar (config in `base.py` UNFOLD dict)
- 19 registered models across all apps

### Content
- 63 projects (5 categories: Routes, Batiments, Hydraulique, Amenagement, Etudes)
- 6 articles, 15 FAQs, 9 team members, 2 site setting images
- Seed: `manage.py seed_projects`, `manage.py seed_content`, `scripts/seed_admin.py`
- All seed commands are idempotent with `--dry-run` support

## Development

```bash
# CSS watch
npm run watch:css

# Django dev server
python manage.py runserver

# Docker
docker-compose up -d   # web:8000, db:5433

# Tests
pytest
```

## Known Gotchas

- `ImageField` default max_length=100 includes upload_to prefix. Slug-based filenames: use `slug[:60]`
- Windows: `self.stdout.write()` crashes on Unicode (cp1252). Use ASCII in management commands
- django-ratelimit 4.x: `from django_ratelimit.decorators import ratelimit`
- django-csp 4.0: dict-style `CONTENT_SECURITY_POLICY = {"DIRECTIVES": {...}}`
- allauth 65.x: `ACCOUNT_LOGIN_METHODS = {"email"}`, `ACCOUNT_SIGNUP_FIELDS = [...]`
- SoftDeleteMixin + AbstractUser: needs diamond-inheritance manager
