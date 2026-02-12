#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser \
        --noinput \
        --username "${DJANGO_SUPERUSER_USERNAME:-admin}" \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        2>/dev/null || true
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn config.wsgi:application -c gunicorn.conf.py
