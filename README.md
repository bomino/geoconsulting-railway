# GeoConsulting SARLU

Website for GeoConsulting SARLU, a civil engineering consulting firm based in Niamey, Niger. ISO 9001:2015 certified. Built with Django 5.1.

## Tech Stack

- **Backend**: Django 5.1, PostgreSQL 16, django-allauth, django-unfold (admin)
- **Frontend**: Tailwind CSS 4, HTMX 2, Alpine.js 3
- **AI**: OpenAI API (streaming chatbot with SSE)
- **Storage**: Cloudflare R2 (via django-storages/boto3)
- **Email**: Resend (via django-anymail)
- **Security**: django-csp, Argon2 password hashing, audit logging

## Apps

| App | Purpose |
|-----|---------|
| `accounts` | Custom user model, email-based auth |
| `core` | Site settings, FAQ, team members, shared mixins |
| `projects` | 63 civil engineering project references |
| `articles` | Blog/news articles with Markdown support |
| `contacts` | Contact form with honeypot spam protection |
| `portal` | Client portal (project tracking, messaging, documents) |
| `crm` | Auto-assignment rules, email templates, CSV export |
| `chatbot` | AI assistant with circuit breaker + rate limiting |
| `audit` | Request/action audit trail |

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Node.js 20+ (for Tailwind CSS)

### Local Development

```bash
# Clone
git clone https://github.com/bomino/geoconsulting.git
cd geoconsulting

# Python env
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements/dev.txt

# Environment
cp .env.example .env
# Edit .env with your DATABASE_URL, DJANGO_SECRET_KEY, etc.

# Database
python manage.py migrate
python manage.py createsuperuser

# Seed data
python scripts/seed_admin.py
python manage.py seed_projects
python manage.py seed_content

# Tailwind CSS
npm install
npm run build:css

# Run
python manage.py runserver
```

### Docker

```bash
docker-compose up -d
# App: http://localhost:8000
# DB: localhost:5433
```

## Project Structure

```
geoconsulting/
├── apps/                  # Django applications
│   ├── accounts/          # User model + auth
│   ├── articles/          # Blog articles
│   ├── audit/             # Audit logging
│   ├── chatbot/           # AI chatbot (OpenAI)
│   ├── contacts/          # Contact form + CRM intake
│   ├── core/              # Site settings, FAQ, team, shared code
│   ├── crm/               # Assignment rules, email templates
│   ├── portal/            # Client portal
│   └── projects/          # Project references
├── config/
│   ├── settings/          # Split settings (base/dev/prod)
│   ├── urls.py
│   └── wsgi.py
├── templates/             # Django templates
│   ├── pages/             # Full page templates
│   ├── partials/          # HTMX partials
│   ├── allauth/           # Auth pages
│   └── base.html
├── static/
│   ├── css/main.css       # Tailwind source
│   └── img/               # Static images
├── requirements/          # Pip requirements (base/dev/prod)
├── Dockerfile             # Multi-stage (Node CSS build + Python)
└── docker-compose.yml     # Dev stack (web + postgres)
```

## Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `DJANGO_SECRET_KEY` | Yes | - |
| `DATABASE_URL` | Yes | `postgres://geo:geo@localhost:5432/geoconsulting` |
| `DJANGO_ALLOWED_HOSTS` | No | `[]` |
| `DEFAULT_FROM_EMAIL` | No | `info@mygeoconsulting.com` |
| `OPENAI_API_KEY` | No | `""` |
| `DJANGO_SETTINGS_MODULE` | No | `config.settings.development` |

## Management Commands

| Command | Purpose |
|---------|---------|
| `seed_projects` | Seed 63 project references |
| `seed_content` | Seed images, articles, FAQs, team members, site settings |

Both commands are idempotent and support `--dry-run`.

## License

Proprietary. All rights reserved.
