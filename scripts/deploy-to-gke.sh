#!/bin/bash

# Script para desplegar HexaBuilders en GKE
# Uso: ./deploy-to-gke.sh PROJECT_ID [CLUSTER_NAME] [ZONE] [TAG]

set -e

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 PROJECT_ID [CLUSTER_NAME] [ZONE] [TAG]"
    echo "Ejemplo: $0 my-hexabuilders-project hexabuilders-cluster us-central1-a v1.0.0"
    exit 1
fi

PROJECT_ID=$1
CLUSTER_NAME=${2:-hexabuilders-cluster}
ZONE=${3:-us-central1-a}
TAG=${4:-latest}

echo "🚀 Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

echo "🔗 Obteniendo credenciales del cluster..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

echo "🏗️ Aplicando configuración de Kubernetes..."

# Reemplazar PROJECT_ID en los archivos de Kubernetes
sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" k8s/*.yaml

# Aplicar configuración
kubectl apply -k k8s/

echo "⏳ Esperando que los pods estén listos..."
kubectl wait --for=condition=ready pod -l app=pulsar-standalone -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgres -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=elasticsearch -n hexabuilders --timeout=300s

echo "⏳ Esperando que los servicios de aplicación estén listos..."
kubectl wait --for=condition=ready pod -l app=partner-management -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=onboarding -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=campaign-management -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=recruitment -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=notifications -n hexabuilders --timeout=300s
kubectl wait --for=condition=ready pod -l app=bff-web -n hexabuilders --timeout=300s

echo "✅ Despliegue completado exitosamente!"
echo ""
echo "📊 Estado de los pods:"
kubectl get pods -n hexabuilders

echo ""
echo "🌐 Servicios disponibles:"
kubectl get services -n hexabuilders

echo ""
echo "🔗 Para acceder al BFF Web:"
echo "  kubectl port-forward service/bff-web-lb 8000:80 -n hexabuilders"
echo "  Luego abrir: http://localhost:8000"

echo ""
echo "📈 Para ver logs:"
echo "  kubectl logs -f deployment/bff-web -n hexabuilders"