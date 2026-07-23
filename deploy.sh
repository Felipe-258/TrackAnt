#!/bin/bash
# TrackAnt Deploy Script
# Ejecutar desde la laptop: ./deploy.sh

REMOTE="felipe@192.168.1.156"
REMOTE_DIR="~/docker/web-apps"
SOCK="/tmp/trackant_deploy_sock"

echo "=== TrackAnt Deploy ==="
echo ""

# Cleanup socket previo
rm -f "$SOCK"

# Primera conexión: autentica y crea socket compartido
echo "[1/4] Conectando al TrueNAS..."
echo "  (Ingresa la contraseña UNA sola vez)"
echo ""
if ! ssh -t -o ConnectTimeout=10 -o ControlMaster=yes -o ControlPath="$SOCK" -o ControlPersist=60 $REMOTE "echo OK" 2>/dev/null; then
    echo "ERROR: No se puede conectar al TrueNAS"
    rm -f "$SOCK"
    echo ""
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo "  Conectado OK"
echo ""

# Ejecutar deploy con -t para que sudo pueda pedir contraseña
echo "[2/4] Ejecutando deploy..."
ssh -t -o ControlPath="$SOCK" $REMOTE "cd $REMOTE_DIR && sudo docker compose pull trackant && sudo docker compose up -d trackant" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo el deploy"
    ssh -o ControlPath="$SOCK" -O exit $REMOTE 2>/dev/null
    rm -f "$SOCK"
    echo ""
    read -p "Presiona Enter para cerrar..."
    exit 1
fi
echo ""

# Verificación
echo "[3/4] Verificando..."
ssh -t -o ControlPath="$SOCK" $REMOTE "cd $REMOTE_DIR && sudo docker compose ps trackant" 2>&1

# Cerrar socket
ssh -o ControlPath="$SOCK" -O exit $REMOTE 2>/dev/null
rm -f "$SOCK"

echo ""
echo "=== Deploy completado ==="
echo "TrackAnt: http://192.168.1.156:3200"
echo ""
read -p "Presiona Enter para cerrar..."
