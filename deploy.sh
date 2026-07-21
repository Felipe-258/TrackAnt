#!/bin/bash
# TrackAnt Deploy Script
# Ejecutar desde la laptop para deployar manualmente

REMOTE="felipe@192.168.1.156"
REMOTE_DIR="~/docker/web-apps"

echo "=== TrackAnt Deploy ==="
echo ""

# Verificar SSH
echo "[1/4] Verificando conexion SSH..."
if ! ssh -o ConnectTimeout=5 $REMOTE "echo OK" 2>/dev/null; then
    echo ""
    echo "ERROR: No se puede conectar al TrueNAS"
    echo "Verifica que:"
    echo "  - El TrueNAS este encendido"
    echo "  - Este en la misma red"
    echo "  - La IP sea correcta: $REMOTE"
    exit 1
fi
echo "  SSH OK"
echo ""

# Verificar Docker
echo "[2/4] Verificando Docker en TrueNAS..."
if ! ssh $REMOTE "docker info" >/dev/null 2>&1; then
    echo ""
    echo "ERROR: Docker no esta corriendo en el TrueNAS"
    echo "Ejecuta en el TrueNAS: sudo service docker start"
    exit 1
fi
echo "  Docker OK"
echo ""

# Pull imagen
echo "[3/4] Descargando ultima imagen..."
echo "  (Si te pide contraseña, es la del TrueNAS)"
echo ""
ssh -t $REMOTE "cd $REMOTE_DIR && sudo docker compose pull trackant" 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: No se pudo descargar la imagen"
    exit 1
fi
echo ""

# Restart contenedor
echo "[4/4] Reiniciando TrackAnt..."
ssh -t $REMOTE "cd $REMOTE_DIR && sudo docker compose up -d trackant" 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: No se pudo reiniciar el contenedor"
    echo "Ver logs: ssh $REMOTE 'cd $REMOTE_DIR && sudo docker compose logs trackant'"
    exit 1
fi

echo ""
echo "Esperando 10 segundos para que arranque..."
sleep 10

# Verificar estado
echo ""
echo "Estado del contenedor:"
ssh $REMOTE "cd $REMOTE_DIR && sudo docker compose ps trackant" 2>/dev/null

echo ""
echo "=== Deploy completado ==="
echo "TrackAnt: http://192.168.1.156:3200"
