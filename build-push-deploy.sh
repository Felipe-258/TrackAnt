#!/bin/bash
# TrackAnt Build + Push + Deploy
# Ejecutar desde la laptop: ./build-push-deploy.sh

set -e

REMOTE="felipe@192.168.1.156"
REMOTE_DIR="~/docker/web-apps"
IMAGE="ghcr.io/felipe-258/trackant"
VERSION=$(cat VERSION | tr -d '[:space:]')

echo "=== TrackAnt Build + Push + Deploy ==="
echo "Version: $VERSION"
echo ""

# Login a GHCR
echo "[1/4] Login a GHCR..."
if ! cat ~/.git-credentials | grep -q github.com; then
    echo "ERROR: No hay credenciales de GitHub configuradas"
    echo "Ejecuta: git config credential.helper store"
    echo "Y haz un push a GitHub para que guarde las credenciales"
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
TOKEN=$(grep 'github.com' ~/.git-credentials | sed 's|https://||;s|@github.com||' | cut -d: -f2-)
echo "$TOKEN" | docker login ghcr.io -u Felipe-258 --password-stdin 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo hacer login a GHCR"
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
ssh $REMOTE "cd $REMOTE_DIR && sudo docker compose ps trackant" 2>/dev/null

echo ""
echo "=== Deploy completado ==="
echo "Version: $VERSION"
echo "TrackAnt: http://192.168.1.156:3200"
echo ""
read -p "Presiona Enter para cerrar..."
