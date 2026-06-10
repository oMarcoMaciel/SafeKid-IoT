#!/bin/bash
# Upload firmware to ESP32 (Scanner)
PORT=$1
if [ -z "$PORT" ]; then
    PORT="/dev/ttyUSB1"
fi

echo "🚀 Iniciando upload para ESP32 (Scanner) em $PORT..."
platformio run -d firmware/esp32 --target upload --upload-port $PORT
