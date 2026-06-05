#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
  echo "🔧 Creando entorno virtual..."
  python3 -m venv venv
  source venv/bin/activate
  pip install --quiet -r requirements.txt
else
  source venv/bin/activate
fi

if [ ! -f "$HOME/.trackant/db.sqlite3" ]; then
  echo "🗄️  Creando base de datos..."
  python manage.py migrate --run-syncdb
  python manage.py seed_data
fi

LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo "🐜 TrackAnt — Servidor iniciado"
echo "   Local:       http://localhost:8000"
echo "   Red:         http://${LOCAL_IP}:8000"
echo "   Admin:       http://localhost:8000/admin/"
echo "   Playground:  http://localhost:8000/ants/playground/"
echo ""

python manage.py runserver 0.0.0.0:8000
