#!/bin/bash
# HexaBuilders - Control de Costos GCP
# Script para apagar/encender servicios y ahorrar dinero

set -e

CLUSTER_NAME="hexabuilders-cluster"
ZONE="us-central1-a"
NAMESPACE="hexabuilders"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo "🏗️  HexaBuilders - Control de Costos GCP"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  shutdown       🛑 Apagar cluster (0 nodos) - Ahorra ~\$25/mes"
    echo "  startup        ✅ Encender cluster (1 nodo)"
    echo "  shutdown-lb    🛑 Eliminar Load Balancer - Ahorra ~\$18/mes adicionales"
    echo "  startup-lb     ✅ Recrear Load Balancer"
    echo "  status         📊 Ver estado actual y costos"
    echo "  costs          💰 Mostrar desglose de costos"
    echo "  destroy        💥 Eliminar TODO (usar con cuidado)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 shutdown        # Apagar para fin de semana"
    echo "  $0 startup         # Encender para trabajar"
    echo "  $0 status          # Ver que está corriendo"
}

# Función para mostrar estado actual
show_status() {
    echo -e "${YELLOW}📊 Estado actual del cluster:${NC}"
    
    # Verificar si el cluster existe
    if ! gcloud container clusters describe $CLUSTER_NAME --zone=$ZONE &>/dev/null; then
        echo -e "${RED}❌ Cluster no existe${NC}"
        return 1
    fi
    
    # Obtener número de nodos
    NODE_COUNT=$(gcloud container clusters describe $CLUSTER_NAME --zone=$ZONE --format="value(currentNodeCount)")
    
    if [ "$NODE_COUNT" = "0" ]; then
        echo -e "${RED}🛑 Cluster APAGADO (0 nodos) - Costo: ~\$0/mes por compute${NC}"
        echo -e "${GREEN}💰 Ahorrando: ~\$25/mes${NC}"
    else
        echo -e "${GREEN}✅ Cluster ENCENDIDO ($NODE_COUNT nodos) - Costo: ~\$25/mes${NC}"
        
        # Verificar pods
        echo -e "${YELLOW}📦 Pods en ejecución:${NC}"
        kubectl get pods -n $NAMESPACE 2>/dev/null || echo "No se puede conectar a kubectl"
    fi
    
    # Verificar Load Balancer
    if kubectl get service partner-management-lb -n $NAMESPACE &>/dev/null; then
        LB_IP=$(kubectl get service partner-management-lb -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pendiente")
        echo -e "${GREEN}🌐 Load Balancer ACTIVO - IP: $LB_IP - Costo: ~\$18/mes${NC}"
    else
        echo -e "${RED}🌐 Load Balancer INACTIVO - Ahorrando: ~\$18/mes${NC}"
    fi
}

# Función para mostrar costos
show_costs() {
    echo -e "${YELLOW}💰 Desglose de Costos (USD/mes):${NC}"
    echo ""
    echo "┌─────────────────────────────┬─────────────┬──────────────┐"
    echo "│ Servicio                    │ Encendido   │ Apagado      │"
    echo "├─────────────────────────────┼─────────────┼──────────────┤"
    echo "│ 🖥️  Cluster GKE (1 nodo e2-small) │ ~\$25/mes   │ \$0/mes      │"
    echo "│ 🌐 Load Balancer            │ ~\$18/mes   │ \$0/mes      │"
    echo "│ 💾 Discos Persistentes      │ ~\$3/mes    │ ~\$3/mes     │"
    echo "│ 📦 Container Registry       │ ~\$0.1/mes  │ ~\$0.1/mes   │"
    echo "├─────────────────────────────┼─────────────┼──────────────┤"
    echo "│ 💰 TOTAL                    │ ~\$46/mes   │ ~\$3/mes     │"
    echo "└─────────────────────────────┴─────────────┴──────────────┘"
    echo ""
    echo -e "${GREEN}💡 Ahorro máximo: ~\$43/mes (93% reducción)${NC}"
}

# Función para apagar cluster
shutdown_cluster() {
    echo -e "${YELLOW}🛑 Apagando cluster (escalando a 0 nodos)...${NC}"
    gcloud container clusters resize $CLUSTER_NAME --num-nodes=0 --zone=$ZONE --quiet
    echo -e "${GREEN}✅ Cluster apagado. Ahorrando ~\$25/mes${NC}"
    echo -e "${YELLOW}ℹ️  Para encender: $0 startup${NC}"
}

# Función para encender cluster
startup_cluster() {
    echo -e "${YELLOW}✅ Encendiendo cluster (escalando a 1 nodo)...${NC}"
    gcloud container clusters resize $CLUSTER_NAME --num-nodes=1 --zone=$ZONE --quiet
    echo -e "${GREEN}✅ Cluster encendido. Esperando que los pods estén listos...${NC}"
    
    # Esperar a que los pods estén listos
    echo -e "${YELLOW}⏳ Esperando pods (esto puede tomar 2-3 minutos)...${NC}"
    sleep 60
    kubectl wait --for=condition=ready pod --all -n $NAMESPACE --timeout=300s || echo "Algunos pods aún se están iniciando"
    
    echo -e "${GREEN}🎉 Sistema listo para usar${NC}"
    
    # Mostrar IP del Load Balancer si existe
    if kubectl get service partner-management-lb -n $NAMESPACE &>/dev/null; then
        LB_IP=$(kubectl get service partner-management-lb -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ ! -z "$LB_IP" ]; then
            echo -e "${GREEN}🌐 Acceso: http://$LB_IP/health${NC}"
        fi
    fi
}

# Función para eliminar Load Balancer
shutdown_lb() {
    echo -e "${YELLOW}🛑 Eliminando Load Balancer...${NC}"
    kubectl delete service partner-management-lb -n $NAMESPACE
    echo -e "${GREEN}✅ Load Balancer eliminado. Ahorrando ~\$18/mes adicionales${NC}"
    echo -e "${YELLOW}ℹ️  Para recrear: $0 startup-lb${NC}"
}

# Función para recrear Load Balancer
startup_lb() {
    echo -e "${YELLOW}✅ Recreando Load Balancer...${NC}"
    kubectl expose deployment partner-management --type=LoadBalancer --port=80 --target-port=5000 --name=partner-management-lb -n $NAMESPACE
    echo -e "${GREEN}✅ Load Balancer creado. Esperando IP externa...${NC}"
    kubectl get service partner-management-lb -n $NAMESPACE -w
}

# Función para eliminar TODO (usar con cuidado)
destroy_all() {
    echo -e "${RED}💥 ADVERTENCIA: Esto eliminará TODO el cluster${NC}"
    read -p "¿Estás seguro? Escribe 'ELIMINAR' para confirmar: " confirm
    if [ "$confirm" = "ELIMINAR" ]; then
        echo -e "${YELLOW}🗑️  Eliminando cluster completo...${NC}"
        gcloud container clusters delete $CLUSTER_NAME --zone=$ZONE --quiet
        echo -e "${GREEN}✅ Cluster eliminado completamente${NC}"
        echo -e "${YELLOW}ℹ️  Las imágenes en Container Registry se mantienen${NC}"
        echo -e "${YELLOW}ℹ️  Para recrear: seguir la guía completa${NC}"
    else
        echo -e "${YELLOW}❌ Cancelado${NC}"
    fi
}

# Main script logic
case "${1:-help}" in
    "shutdown")
        shutdown_cluster
        ;;
    "startup")
        startup_cluster
        ;;
    "shutdown-lb")
        shutdown_lb
        ;;
    "startup-lb")
        startup_lb
        ;;
    "status")
        show_status
        ;;
    "costs")
        show_costs
        ;;
    "destroy")
        destroy_all
        ;;
    "help"|*)
        show_help
        ;;
esac
