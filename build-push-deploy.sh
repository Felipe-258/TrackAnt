#!/bin/bash
# TrackAnt Build + Push + Deploy
# Ejecutar desde la laptop: ./build-push-deploy.sh

REMOTE="felipe@192.168.1.156"
REMOTE_DIR="~/docker/web-apps"
IMAGE="ghcr.io/felipe-258/trackant"
CURRENT_VERSION=$(cat VERSION | tr -d '[:space:]')

ensure_docker() {
    if docker info >/dev/null 2>&1; then
        echo "  Docker daemon OK"
        return 0
    fi
    echo "  Docker daemon no está corriendo. Intentando arrancarlo..."
    sudo systemctl start docker 2>/dev/null || sudo service docker start 2>/dev/null || {
        sudo dockerd >/dev/null 2>&1 &
    }
    sleep 3
    if docker info >/dev/null 2>&1; then
        echo "  Docker daemon arrancado"
        return 0
    fi
    echo "ERROR: No se pudo iniciar el Docker daemon. Arrancalo manualmente con: sudo systemctl start docker"
    read -p "Presiona Enter para cerrar..."
    exit 1
}

echo "=== TrackAnt Build + Push + Deploy ==="
echo "Versión actual: $CURRENT_VERSION"
echo ""
echo "[0/4] Verificando Docker daemon..."
ensure_docker
echo ""
read -p "Nueva versión (Enter para mantener $CURRENT_VERSION): " NEW_VERSION
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
fi
echo "$NEW_VERSION" > VERSION
VERSION=$NEW_VERSION
echo "  Versión a buildear: $VERSION"
echo ""

# Login a GHCR
echo "[1/4] Login a GHCR..."
if [ ! -f ~/.ghcr_token ]; then
    echo "ERROR: No existe ~/.ghcr_token"
    echo "Ejecuta: echo 'TU_TOKEN' > ~/.ghcr_token && chmod 600 ~/.ghcr_token"
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
TOKEN=$(cat ~/.ghcr_token | tr -d '[:space:]')
if [ "$TOKEN" = "TU_TOKEN_AQUI" ] || [ -z "$TOKEN" ]; then
    echo "ERROR: ~/.ghcr_token tiene el placeholder. Reemplazá 'TU_TOKEN_AQUI' con tu token real."
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "$TOKEN" | docker login ghcr.io -u Felipe-258 --password-stdin 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo hacer login a GHCR. Verificá que el token tenga permisos write:packages."
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "  Login OK"
echo ""

# Build
echo "[2/4] Buildeando imagen Docker..."
docker build -t $IMAGE:latest -t $IMAGE:$VERSION . 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo el build"
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "  Build OK"
echo ""

# Push
echo "[3/4] Subiendo imagen a GHCR..."
docker push $IMAGE:latest 2>&1
docker push $IMAGE:$VERSION 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo el push a GHCR"
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "  Push OK"
echo ""

# Deploy
echo "[4/4] Deployando en TrueNAS..."
echo "  (Te va a pedir la contraseña del TrueNAS)"
echo ""
ssh -t $REMOTE "cd $REMOTE_DIR && sudo docker compose pull trackant && sudo docker compose up -d trackant" 2>&1

echo ""
echo "Esperando 10 segundos para que arranque..."
sleep 10

echo ""
echo "Estado del contenedor:"
ssh $REMOTE "cd $REMOTE_DIR && sudo docker compose ps trackant" 2>/dev/null || true

echo ""
echo "=== Deploy completado ==="
echo "Version: $VERSION"
echo "TrackAnt: http://192.168.1.156:3200"
echo ""
echo "Si ves algún error arriba, copialo antes de continuar."
read -p "Presiona Enter para cerrar..."
