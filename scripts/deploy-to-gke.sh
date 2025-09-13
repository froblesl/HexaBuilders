#!/bin/bash

# Script para desplegar HexaBuilders en Google Kubernetes Engine (GKE)
# Uso: ./deploy-to-gke.sh PROJECT_ID CLUSTER_NAME [ZONE]

set -e

if [ "$#" -lt 2 ]; then
    echo "Uso: $0 PROJECT_ID CLUSTER_NAME [ZONE]"
    echo "Ejemplo: $0 my-hexabuilders-project hexabuilders-cluster us-central1-a"
    exit 1
fi

PROJECT_ID=$1
CLUSTER_NAME=$2
ZONE=${3:-us-central1-a}

echo "🚀 Conectando al cluster GKE..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project=$PROJECT_ID

echo "📝 Actualizando manifiestos con PROJECT_ID..."
# Crear una copia temporal de kustomization.yaml con el PROJECT_ID correcto
cp k8s/kustomization.yaml k8s/kustomization.yaml.bak
sed "s/PROJECT_ID/$PROJECT_ID/g" k8s/kustomization.yaml.bak > k8s/kustomization.yaml

# También actualizar los deployments
sed "s/PROJECT_ID/$PROJECT_ID/g" k8s/partner-management-deployment.yaml > k8s/partner-management-deployment.yaml.tmp
mv k8s/partner-management-deployment.yaml.tmp k8s/partner-management-deployment.yaml

sed "s/PROJECT_ID/$PROJECT_ID/g" k8s/notifications-deployment.yaml > k8s/notifications-deployment.yaml.tmp
mv k8s/notifications-deployment.yaml.tmp k8s/notifications-deployment.yaml

echo "📦 Desplegando con Kustomize..."
kubectl apply -k k8s/

echo "⏳ Esperando a que los pods estén listos..."
kubectl wait --namespace=hexabuilders --for=condition=ready pod --selector=app=postgres --timeout=300s
kubectl wait --namespace=hexabuilders --for=condition=ready pod --selector=app=zookeeper --timeout=300s
kubectl wait --namespace=hexabuilders --for=condition=ready pod --selector=app=broker --timeout=300s
kubectl wait --namespace=hexabuilders --for=condition=ready pod --selector=app=partner-management --timeout=300s

echo "🌍 Obteniendo IP del Load Balancer..."
kubectl get service partner-management-lb -n hexabuilders

echo "✅ Despliegue completado!"
echo ""
echo "Para verificar el estado:"
echo "  kubectl get all -n hexabuilders"
echo ""
echo "Para ver los logs:"
echo "  kubectl logs -n hexabuilders -l app=partner-management"
echo ""
echo "Para probar la API:"
echo "  export LOAD_BALANCER_IP=\$(kubectl get service partner-management-lb -n hexabuilders -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "  curl http://\$LOAD_BALANCER_IP/health"

# Restaurar el archivo original
mv k8s/kustomization.yaml.bak k8s/kustomization.yaml
