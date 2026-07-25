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

echo "Checking daily backup..."
TODAY=$(date +%Y-%m-%d)
BACKUP_DIR="/root/.trackant/backups"
mkdir -p "$BACKUP_DIR"
if ls "$BACKUP_DIR"/backup_${TODAY}_*.sqlite3 1>/dev/null 2>&1; then
    echo "Backup already done today, skipping."
else
    echo "No backup today, creating one..."
    python manage.py backup_db 2>&1 || true
fi

echo "Starting Gunicorn..."
exec "$@"
