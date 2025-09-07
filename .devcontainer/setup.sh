#!/bin/bash

echo "[*] Installing Python dependencies..."
pip install -r requirements.txt
pip install -r pulsar-requirements.txt

echo "[*] Building Docker images..."
docker build . -f partner-management.Dockerfile -t hexabuilders/partner-management
docker build . -f notifications.Dockerfile -t hexabuilders/notifications

echo "[*] Pulling docker-compose dependencies..."
docker-compose pull

echo "[✓] Dev container setup completed successfully."