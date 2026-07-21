#!/bin/bash
set -e

echo "=== TrackAnt starting ==="

echo "Running migrations..."
if python manage.py migrate --noinput 2>&1; then
    echo "Migrations applied successfully."
else
    echo "WARNING: Migrations failed. Check logs above."
fi

echo "Checking if seed data is needed..."
python manage.py seed_data 2>/dev/null || true

echo "Starting Gunicorn..."
exec "$@"
