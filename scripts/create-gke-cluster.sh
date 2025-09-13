#!/bin/bash

# Script para crear un cluster GKE para HexaBuilders
# Uso: ./create-gke-cluster.sh PROJECT_ID [CLUSTER_NAME] [ZONE]

set -e

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 PROJECT_ID [CLUSTER_NAME] [ZONE]"
    echo "Ejemplo: $0 my-hexabuilders-project hexabuilders-cluster us-central1-a"
    exit 1
fi

PROJECT_ID=$1
CLUSTER_NAME=${2:-hexabuilders-cluster}
ZONE=${3:-us-central1-a}

echo "🚀 Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

echo "🔧 Habilitando APIs necesarias..."
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo "🏗️ Creando cluster GKE..."
gcloud container clusters create $CLUSTER_NAME \
    --zone=$ZONE \
    --machine-type=e2-standard-4 \
    --num-nodes=3 \
    --disk-size=50GB \
    --disk-type=pd-standard \
    --enable-cloud-logging \
    --enable-cloud-monitoring \
    --enable-autorepair \
    --enable-autoupgrade \
    --maintenance-window-start="2024-01-01T04:00:00Z" \
    --maintenance-window-end="2024-01-01T08:00:00Z" \
    --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SA"

echo "🔗 Obteniendo credenciales del cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

echo "✅ Cluster GKE creado exitosamente!"
echo "Nombre: $CLUSTER_NAME"
echo "Zona: $ZONE"
echo "Proyecto: $PROJECT_ID"
echo ""
echo "Para conectarte al cluster:"
echo "  gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "Para ver los nodos:"
echo "  kubectl get nodes"
