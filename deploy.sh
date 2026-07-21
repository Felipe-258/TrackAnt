#!/bin/bash
# TrackAnt Deploy Script
# Ejecutar desde la laptop para deployar manualmente

set -e

echo "=== TrackAnt Deploy ==="
echo ""

# Verificar SSH
echo "Verificando conexion SSH..."
if ! ssh -o ConnectTimeout=5 felipe@192.168.1.156 "echo OK" 2>/dev/null; then
    echo "ERROR: No se puede conectar al TrueNAS"
    echo "Verifica que este encendido y en la red"
    exit 1
fi
echo "SSH OK"
echo ""

# Pull y restart
echo "Descargando ultima imagen..."
ssh felipe@192.168.1.156 "cd ~/docker/web-apps && sudo docker compose pull trackant"

echo "Reiniciando TrackAnt..."
ssh felipe@192.168.1.156 "cd ~/docker/web-apps && sudo docker compose up -d trackant"

echo "Esperando 10 segundos..."
sleep 10

echo "Verificando contenedor..."
ssh felipe@192.168.1.156 "cd ~/docker/web-apps && sudo docker compose ps trackant"

echo ""
echo "=== Deploy completado ==="
echo "TrackAnt: http://192.168.1.156:3200"
