#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 2 \
    --timeout 120
