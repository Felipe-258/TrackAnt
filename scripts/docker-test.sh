#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE="trackant-local"
CONTAINER="trackant-test"
PORT=${1:-8000}

cd "$PROJECT_DIR"

echo "========================================"
echo "  🐜 TrackAnt — Docker test"
echo "========================================"
echo ""

# Build
echo "[1/3] Building Docker image..."
if ! docker build -t $IMAGE . 2>&1; then
    echo ""
    echo "ERROR: Docker build failed."
    echo "Asegurate de tener Docker instalado y corriendo."
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "  Build OK"

# Clean old container
docker rm -f $CONTAINER 2>/dev/null || true

# Run
mkdir -p $HOME/.trackant
echo ""
echo "[2/3] Starting container on port $PORT..."
if ! docker run -d --name $CONTAINER \
  -p $PORT:8000 \
  -v $HOME/.trackant:/root/.trackant \
  $IMAGE 2>&1; then
    echo ""
    echo "ERROR: No se pudo iniciar el contenedor."
    echo "  Posibles causas:"
    echo "  - Puerto $PORT ocupado (cambialo: ./scripts/docker-test.sh 8080)"
    echo "  - El contenedor '$CONTAINER' ya existe (docker rm -f $CONTAINER)"
    echo "  - Docker no tiene permisos suficientes"
    read -p "Presiona Enter para cerrar..."
    exit 1
fi

# Wait for startup
echo "  Esperando que arranque..."
for i in $(seq 1 15); do
    if docker logs $CONTAINER 2>&1 | grep -q 'Booting worker'; then
        echo "  Container ready!"
        break
    fi
    sleep 1
done

echo ""
echo "[3/3] ✅ Listo!"
echo ""

LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo "  Local:       http://localhost:$PORT"
echo "  Red:         http://${LOCAL_IP}:$PORT"
echo "  Admin:       http://localhost:$PORT/admin/"
echo "  Cuotas:      http://localhost:$PORT/cuotas/"
echo ""
echo "  Para procesar vencimientos:"
echo "    docker exec -it $CONTAINER python manage.py process_recurring"
echo ""
echo "  Para detener: docker stop $CONTAINER && docker rm $CONTAINER"
echo ""

read -p "Presiona Enter para cerrar..."
