#!/bin/bash
set -e

export PORT="${PORT:-8000}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

exec "$@"
