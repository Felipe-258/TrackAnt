#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
source venv/bin/activate

echo "🐜 TrackAnt — Servidor de desarrollo"
echo "   http://localhost:8000"
echo ""

python manage.py runserver 0.0.0.0:8000
