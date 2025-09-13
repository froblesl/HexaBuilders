# HexaBuilders - Despliegue en Kubernetes (GCP)

Este documento describe cómo desplegar HexaBuilders en Google Kubernetes Engine (GKE).

## Prerrequisitos

1. **Google Cloud SDK** instalado y configurado
2. **kubectl** instalado
3. **Docker** instalado
4. Una cuenta de GCP con permisos para crear clusters y usar Container Registry

## Instalación de Prerrequisitos

```bash
# Instalar Google Cloud SDK (macOS)
brew install --cask google-cloud-sdk

# Inicializar gcloud
gcloud init

# Instalar kubectl
gcloud components install kubectl

# Verificar Docker
docker version
```

## Estructura del Despliegue

```
k8s/
├── namespace.yaml                    # Namespace hexabuilders
├── postgres-secret.yaml             # Credenciales PostgreSQL
├── postgres-pvc.yaml                # Volumen persistente
├── postgres-configmap.yaml          # Configuración base de datos
├── postgres-deployment.yaml         # PostgreSQL deployment
├── pulsar-zookeeper.yaml           # Apache Zookeeper
├── pulsar-bookie.yaml               # Apache BookKeeper
├── pulsar-broker.yaml               # Apache Pulsar Broker
├── partner-management-deployment.yaml # Aplicación principal
├── notifications-deployment.yaml    # Servicio de notificaciones
└── kustomization.yaml               # Kustomize config

scripts/
├── create-gke-cluster.sh            # Crear cluster GKE
├── build-and-push-images.sh         # Construir y subir imágenes
├── deploy-to-gke.sh                 # Desplegar aplicación
└── cleanup-gke.sh                   # Limpiar recursos
```

## Comandos de Despliegue

### 1. Crear Proyecto en GCP (Opcional)

```bash
# Crear nuevo proyecto
PROJECT_ID="hexabuilders-$(date +%s)"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Habilitar facturación (requerido)
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

### 2. Crear Cluster GKE

```bash
# Opción A: Usar nuestro script automatizado
./scripts/create-gke-cluster.sh $PROJECT_ID

# Opción B: Comando manual completo
gcloud container clusters create hexabuilders-cluster \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --num-nodes=3 \
    --enable-cloud-logging \
    --enable-cloud-monitoring
```

### 3. Construir y Subir Imágenes Docker

```bash
# Configurar autenticación de Docker
gcloud auth configure-docker

# Construir y subir imágenes
./scripts/build-and-push-images.sh $PROJECT_ID
```

### 4. Desplegar Aplicación

```bash
# Desplegar HexaBuilders en GKE
./scripts/deploy-to-gke.sh $PROJECT_ID hexabuilders-cluster us-central1-a
```

### 5. Verificar Despliegue

```bash
# Ver todos los recursos
kubectl get all -n hexabuilders

# Ver estado de los pods
kubectl get pods -n hexabuilders

# Ver logs de la aplicación
kubectl logs -n hexabuilders -l app=partner-management

# Obtener IP del Load Balancer
kubectl get service partner-management-lb -n hexabuilders
```

### 6. Probar la Aplicación

```bash
# Obtener IP externa
LOAD_BALANCER_IP=$(kubectl get service partner-management-lb -n hexabuilders -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Probar health check
curl http://$LOAD_BALANCER_IP/health

# Crear un partner
curl -X POST http://$LOAD_BALANCER_IP/api/v1/partners-comando \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Partner K8s",
    "email": "test-k8s@example.com", 
    "telefono": "+57-300-1234567",
    "tipo_partner": "INDIVIDUAL"
  }'

# Consultar partners
curl http://$LOAD_BALANCER_IP/api/v1/partners-query
```

## Comandos de Monitoreo y Debug

### Ver Estado de los Servicios

```bash
# Pods en ejecución
kubectl get pods -n hexabuilders -w

# Servicios y sus endpoints
kubectl get services -n hexabuilders

# Eventos del cluster
kubectl get events -n hexabuilders --sort-by='.lastTimestamp'

# Descripción detallada de un pod
kubectl describe pod <POD_NAME> -n hexabuilders
```

### Ver Logs

```bash
# Logs de PostgreSQL
kubectl logs -n hexabuilders -l app=postgres

# Logs de Apache Pulsar
kubectl logs -n hexabuilders -l app=broker

# Logs de la aplicación principal
kubectl logs -n hexabuilders -l app=partner-management -f

# Logs de notificaciones
kubectl logs -n hexabuilders -l app=notifications
```

### Acceder a los Contenedores

```bash
# Conectar a PostgreSQL
kubectl exec -it -n hexabuilders deployment/postgres -- psql -U hexabuilders_user -d hexabuilders

# Ver archivos en el contenedor de la aplicación
kubectl exec -it -n hexabuilders deployment/partner-management -- bash
```

## Escalado y Performance

### Escalar la Aplicación

```bash
# Escalar partner-management a 5 réplicas
kubectl scale deployment partner-management -n hexabuilders --replicas=5

# Escalar el cluster (añadir nodos)
gcloud container clusters resize hexabuilders-cluster --num-nodes=5 --zone=us-central1-a
```

### Auto-escalado

```bash
# Habilitar auto-escalado horizontal de pods
kubectl autoscale deployment partner-management -n hexabuilders --cpu-percent=50 --min=2 --max=10

# Ver estado del auto-escalado
kubectl get hpa -n hexabuilders
```

## Limpieza de Recursos

### Eliminar Solo la Aplicación

```bash
# Eliminar namespace (mantiene cluster)
kubectl delete namespace hexabuilders
```

### Eliminar Todo

```bash
# Usar nuestro script de limpieza
./scripts/cleanup-gke.sh $PROJECT_ID

# O comandos manuales
kubectl delete namespace hexabuilders
gcloud container clusters delete hexabuilders-cluster --zone=us-central1-a
```

## Costos y Consideraciones

### Estimación de Costos (USD/mes)

- **Cluster GKE**: ~$73/mes (3 nodos e2-standard-4)
- **Load Balancer**: ~$18/mes
- **Disco persistente**: ~$1/mes (10GB)
- **Container Registry**: ~$0.1/mes
- **Total**: ~$92/mes

### Optimización de Costos

```bash
# Usar nodos preemptibles (más baratos)
gcloud container clusters create hexabuilders-cluster \
    --preemptible \
    --machine-type=e2-medium \
    --num-nodes=2

# Programar escalado automático del cluster
gcloud container clusters update hexabuilders-cluster \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --zone=us-central1-a
```

## Resolución de Problemas

### Problemas Comunes

1. **ImagePullError**: Las imágenes no se subieron correctamente
   ```bash
   ./scripts/build-and-push-images.sh $PROJECT_ID
   ```

2. **PostgreSQL no inicia**: Problemas con volúmenes persistentes
   ```bash
   kubectl delete pvc postgres-pvc -n hexabuilders
   kubectl apply -k k8s/
   ```

3. **Load Balancer sin IP**: Esperar unos minutos más
   ```bash
   kubectl get service partner-management-lb -n hexabuilders -w
   ```

### Logs de Debug

```bash
# Ver todos los eventos de error
kubectl get events -n hexabuilders --field-selector type=Warning

# Logs detallados de un pod que falla
kubectl logs -n hexabuilders <POD_NAME> --previous
```

## URLs Útiles

- **GCP Console**: https://console.cloud.google.com
- **Kubernetes Dashboard**: `kubectl proxy` → http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
- **Container Registry**: https://console.cloud.google.com/gcr

## Seguridad

### Network Policies (Opcional)

```bash
# Aplicar políticas de red restrictivas
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hexabuilders-network-policy
  namespace: hexabuilders
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: hexabuilders
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: hexabuilders
EOF
```

### Secrets Management

```bash
# Rotar secretos de PostgreSQL
kubectl create secret generic postgres-secret-new \
  --from-literal=POSTGRES_USER=nuevo_usuario \
  --from-literal=POSTGRES_PASSWORD=nueva_password \
  --from-literal=POSTGRES_DB=hexabuilders \
  -n hexabuilders

# Actualizar deployment para usar nuevos secretos
kubectl patch deployment postgres -n hexabuilders \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"postgres","envFrom":[{"secretRef":{"name":"postgres-secret-new"}}]}]}}}}'
```
