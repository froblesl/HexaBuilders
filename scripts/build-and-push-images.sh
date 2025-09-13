#!/bin/bash

# Script para construir y subir las imágenes Docker a Google Container Registry
# Uso: ./build-and-push-images.sh PROJECT_ID

set -e

if [ "$#" -ne 1 ]; then
    echo "Uso: $0 PROJECT_ID"
    echo "Ejemplo: $0 my-hexabuilders-project"
    exit 1
fi

PROJECT_ID=$1
REGION="us-central1"

echo "🚀 Configurando Docker para GCP..."
gcloud auth configure-docker

echo "🏗️ Construyendo imagen de Partner Management..."
docker build -t gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest -f partner-management.Dockerfile .

echo "🏗️ Construyendo imagen de Notifications..."
docker build -t gcr.io/$PROJECT_ID/hexabuilders-notifications:latest -f notifications.Dockerfile .

echo "📤 Subiendo imagen de Partner Management..."
docker push gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest

echo "📤 Subiendo imagen de Notifications..."
docker push gcr.io/$PROJECT_ID/hexabuilders-notifications:latest

echo "✅ Imágenes construidas y subidas exitosamente!"
echo "Partner Management: gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest"
echo "Notifications: gcr.io/$PROJECT_ID/hexabuilders-notifications:latest"
