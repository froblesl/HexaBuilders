#!/bin/bash

# Script para construir y subir imágenes Docker a GCR
# Uso: ./build-and-push-images.sh PROJECT_ID [TAG]

set -e

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 PROJECT_ID [TAG]"
    echo "Ejemplo: $0 my-hexabuilders-project v1.0.0"
    exit 1
fi

PROJECT_ID=$1
TAG=${2:-latest}

echo "🚀 Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

echo "🔧 Configurando Docker para GCR..."
gcloud auth configure-docker

echo "🏗️ Construyendo y subiendo imágenes..."

# Construir y subir Partner Management
echo "📦 Construyendo partner-management..."
docker build -f src/partner_management/Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-partner-management:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-partner-management:$TAG

# Construir y subir Onboarding
echo "📦 Construyendo onboarding..."
docker build -f src/onboarding/Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-onboarding:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-onboarding:$TAG

# Construir y subir Campaign Management
echo "📦 Construyendo campaign-management..."
docker build -f src/campaign_management/Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-campaign-management:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-campaign-management:$TAG

# Construir y subir Recruitment
echo "📦 Construyendo recruitment..."
docker build -f src/recruitment/Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-recruitment:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-recruitment:$TAG

# Construir y subir Notifications
echo "📦 Construyendo notifications..."
docker build -f notifications.Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-notifications:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-notifications:$TAG

# Construir y subir BFF Web
echo "📦 Construyendo bff-web..."
docker build -f bff_web.Dockerfile -t gcr.io/$PROJECT_ID/hexabuilders-bff-web:$TAG .
docker push gcr.io/$PROJECT_ID/hexabuilders-bff-web:$TAG

echo "✅ Todas las imágenes construidas y subidas exitosamente!"
echo "Proyecto: $PROJECT_ID"
echo "Tag: $TAG"
echo ""
echo "Para desplegar en Kubernetes:"
echo "  kubectl apply -k k8s/"