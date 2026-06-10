#!/bin/bash
# View logs wirelessly via MQTT (using Docker)
DEVICE=$1
CONTAINER="rfid-mosquitto"

if [ "$DEVICE" == "esp32" ]; then
    echo "📋 Mostrando logs REMOTOS do ESP32 (Scanner)..."
    docker exec $CONTAINER mosquitto_sub -h localhost -t "logs/esp32" -v
elif [ "$DEVICE" == "wemos" ]; then
    echo "📋 Mostrando logs REMOTOS do Wemos (Tag)..."
    docker exec $CONTAINER mosquitto_sub -h localhost -t "logs/wemos" -v
elif [ "$DEVICE" == "all" ]; then
    echo "📋 Mostrando TODOS os logs remotos..."
    docker exec $CONTAINER mosquitto_sub -h localhost -t "logs/#" -v
else
    echo "Uso: ./scripts/view_logs.sh [esp32|wemos|all]"
    echo "Exemplo: ./scripts/view_logs.sh all"
fi
