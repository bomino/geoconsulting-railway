#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn config.wsgi:application -c gunicorn.conf.py
