#!/bin/sh
set -e

echo "Running migrations..."
cd dropme
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn dropme.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 3
