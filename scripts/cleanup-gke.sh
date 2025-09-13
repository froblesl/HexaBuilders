#!/bin/bash

# Script para limpiar recursos GKE de HexaBuilders
# Uso: ./cleanup-gke.sh PROJECT_ID [CLUSTER_NAME] [ZONE]

set -e

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 PROJECT_ID [CLUSTER_NAME] [ZONE]"
    echo "Ejemplo: $0 my-hexabuilders-project hexabuilders-cluster us-central1-a"
    exit 1
fi

PROJECT_ID=$1
CLUSTER_NAME=${2:-hexabuilders-cluster}
ZONE=${3:-us-central1-a}

echo "🚨 ADVERTENCIA: Este script eliminará todos los recursos de HexaBuilders"
echo "Proyecto: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Zona: $ZONE"
echo ""
read -p "¿Estás seguro que quieres continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo "🗑️ Eliminando aplicación de Kubernetes..."
kubectl delete namespace hexabuilders --ignore-not-found=true

echo "🗑️ Eliminando cluster GKE..."
gcloud container clusters delete $CLUSTER_NAME --zone=$ZONE --project=$PROJECT_ID --quiet

echo "🗑️ Eliminando imágenes de Container Registry (opcional)..."
read -p "¿Eliminar también las imágenes de GCR? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    gcloud container images delete gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest --quiet --force-delete-tags || true
    gcloud container images delete gcr.io/$PROJECT_ID/hexabuilders-notifications:latest --quiet --force-delete-tags || true
    echo "🗑️ Imágenes eliminadas"
fi

echo "✅ Limpieza completada!"
