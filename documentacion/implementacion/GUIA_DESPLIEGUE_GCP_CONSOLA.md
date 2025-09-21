# Guía de Despliegue HexaBuilders en GCP

## 🎯 Prerrequisitos

1. **Cuenta de Google Cloud** con créditos gratuitos o facturación habilitada
2. **Proyecto de GCP** creado (o lo crearemos en el paso 1)

---

## 📋 PASO A PASO

### **PASO 1: Crear/Configurar Proyecto en GCP**

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. En la barra superior, haz clic en **"Select a project"** 
3. Clic en **"NEW PROJECT"**
4. **Project name**: `example`
5. **Location**: Déjalo en blanco o usa tu organización
6. Clic en **"CREATE"**
7. Espera a que se cree y **selecciona el proyecto**

### **PASO 2: Habilitar APIs Necesarias**

1. En el menú lateral, ve a **"APIs & Services" > "Library"**
2. Busca y habilita estas APIs (clic en cada una y luego "ENABLE"):
   - **Kubernetes Engine API**
   - **Container Registry API** 
   - **Compute Engine API**
   - **Cloud Build API**

### **PASO 3: Crear Cluster de Kubernetes (GKE)**

1. **"Kubernetes Engine" > "Clusters"**
2. Clic en **"CREATE"** 
3. **"GKE Standard"**
4. **Cluster basics**:
   - **Name**: `hexabuilders-cluster`
   - **Location type**: `Zonal`
   - **Zone**: `us-central1-a` (más barato)
5. **Default pool** (lado izquierdo):
   - Clic en **"Nodes"** en el menú lateral
   - **Machine configuration**:
     - **Series**: E2
     - **Machine type**: `e2-small` (2 vCPU, 2GB RAM) - ⚡ Optimizado para costos
   - **Number of nodes**: `1` - ⚡ Mínimo para costos académicos
   - **Disk type**: `Standard persistent disk`
   - **Disk size**: `20 GB` - ⚡ Mínimo necesario
6. **Cluster** (lado izquierdo):
   - Clic en **"Security"**
   - **Enable Workload Identity**: ✅ (recomendado)
7. Clic en **"CREATE"** 
8. ⏱️ **Esperar 5-8 minutos** hasta que aparezca el ✅ verde

### **PASO 4: Configurar kubectl (Cloud Shell)**

1. En la esquina superior derecha, clic en el ícono de **"Cloud Shell"** (>_)
2. En la terminal que aparece, ejecuta:
```bash
# Conectar kubectl al cluster
gcloud container clusters get-credentials hexabuilders-cluster --zone=us-central1-a

# Verificar conexión
kubectl get nodes
```
3. Deberías ver tu nodo listado como "Ready"

### **PASO 5: Construir y Subir Imágenes Docker**

En **Cloud Shell**, ejecuta estos comandos:

```bash
# 1. Clonar el repositorio (si no lo tienes)
git clone https://github.com/froblesl/HexaBuilders.git
cd HexaBuilders

# 2. Obtener PROJECT_ID
export PROJECT_ID=$(gcloud config get-value project)
echo "PROJECT_ID: $PROJECT_ID"

# 3. Configurar autenticación de Docker
gcloud auth configure-docker

# 4. Construir y subir imágenes
# Partner Management
docker build -t gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest -f src/partner_management/Dockerfile .
docker push gcr.io/$PROJECT_ID/hexabuilders-partner-management:latest

# Onboarding
docker build -t gcr.io/$PROJECT_ID/hexabuilders-onboarding:latest -f src/onboarding/Dockerfile .
docker push gcr.io/$PROJECT_ID/hexabuilders-onboarding:latest

# Recruitment
docker build -t gcr.io/$PROJECT_ID/hexabuilders-recruitment:latest -f src/recruitment/Dockerfile .
docker push gcr.io/$PROJECT_ID/hexabuilders-recruitment:latest

# Campaign Management
docker build -t gcr.io/$PROJECT_ID/hexabuilders-campaign-management:latest -f src/campaign_management/Dockerfile .
docker push gcr.io/$PROJECT_ID/hexabuilders-campaign-management:latest

# Notifications
docker build -t gcr.io/$PROJECT_ID/hexabuilders-notifications:latest -f notifications.Dockerfile .
docker push gcr.io/$PROJECT_ID/hexabuilders-notifications:latest
```

### **PASO 6: Actualizar Configuraciones de Kubernetes**

En **Cloud Shell**:

```bash
# Reemplazar PROJECT_ID en los archivos de Kubernetes
find k8s/ -name "*.yaml" -exec sed -i "s/PROJECT_ID/$PROJECT_ID/g" {} \;

# Verificar que se reemplazó correctamente
grep -r "gcr.io/$PROJECT_ID" k8s/
```

### **PASO 7: Desplegar la Aplicación**

En **Cloud Shell**:

```bash
# Desplegar todos los recursos
kubectl apply -k k8s/

# Verificar que todos los recursos se crearon
kubectl get all -n hexabuilders
```

### **PASO 8: Verificar el Despliegue**

1. En **Cloud Shell**:
```bash
# Ver estado de los pods
kubectl get pods -n hexabuilders

# Esperar hasta que todos estén "Running" (puede tomar 5-10 minutos)
kubectl get pods -n hexabuilders -w
```

2. **Obtener IP del Load Balancer**:
```bash
kubectl get service partner-management-lb -n hexabuilders
```

### **PASO 9: Probar la Aplicación**

1. En **Cloud Shell**, usa la IP externa del Load Balancer:
```bash
# Obtener IP externa (esperar hasta que aparezca)
EXTERNAL_IP=$(kubectl get service partner-management-lb -n hexabuilders -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"

# Probar health check
curl http://$EXTERNAL_IP/health

# Crear un partner de prueba
curl -X POST http://$EXTERNAL_IP/api/v1/partners-comando \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Partner GCP Test",
    "email": "test-gcp@example.com", 
    "telefono": "+57-300-9876543",
    "tipo_partner": "INDIVIDUAL"
  }'

# Consultar partners
curl http://$EXTERNAL_IP/api/v1/partners-query
```

---

## 🔍 Monitoreo y Debug

### **Ver Estado de Servicios (Consola Web)**

1. Ve a **"Kubernetes Engine" > "Workloads"**
2. Filtra por namespace **"hexabuilders"**
3. Puedes ver el estado de cada deployment

### **Ver Logs (Consola Web)**

1. En **"Workloads"**, haz clic en cualquier servicio
2. Ve a la pestaña **"Logs"**
3. Selecciona el contenedor específico

### **Ver Logs (Cloud Shell)**

```bash
# Logs de partner-management
kubectl logs -n hexabuilders -l app=partner-management -f

# Logs de PostgreSQL
kubectl logs -n hexabuilders -l app=postgres

# Eventos del cluster
kubectl get events -n hexabuilders --sort-by='.lastTimestamp'
```

---

## 🛠️ Resolución de Problemas Comunes

### **Problema 1: Pods en estado "Pending"**
- **Causa**: Recursos insuficientes
- **Solución**: Ve a "Kubernetes Engine > Clusters", clic en tu cluster, luego "RESIZE" y aumenta a 2 nodos

### **Problema 2: ImagePullError**
- **Causa**: Las imágenes no se subieron correctamente
- **Solución**: Ejecuta de nuevo los comandos de construcción del Paso 5

### **Problema 3: Load Balancer sin IP externa**
- **Causa**: Puede tomar hasta 5 minutos en asignarse
- **Solución**: Esperar o verificar con:
```bash
kubectl describe service partner-management-lb -n hexabuilders
```

### **Problema 4: Aplicación retorna errores 500**
- **Causa**: Problemas con base de datos o Pulsar
- **Solución**: Verificar logs:
```bash
kubectl logs -n hexabuilders -l app=postgres
kubectl logs -n hexabuilders -l app=broker
```

### **MÉTODO 1: Escalar Cluster a 0 (Recomendado) 💰**

**Desde Cloud Shell:**
```bash
gcloud container clusters resize hexabuilders-cluster --num-nodes=0 --zone=us-central1-a

# ✅ ENCENDER: Restaurar 1 nodo cuando necesites
gcloud container clusters resize hexabuilders-cluster --num-nodes=1 --zone=us-central1-a
```

**Desde Consola Web:**
1. Ve a **"Kubernetes Engine" > "Clusters"**
2. Clic en **"hexabuilders-cluster"**
3. Clic en **"RESIZE"**
4. **Cambiar "Number of nodes"** a `0` para apagar o `1` para encender
5. Clic en **"RESIZE"**
---

docker build -t gcr.io/${PROJECT_ID}/onboarding:v11-corrected -f src/onboarding/Dockerfile .
docker build -t gcr.io/${PROJECT_ID}/partner-management:v4-corrected -f src/partner_management/Dockerfile .
docker build -t gcr.io/${PROJECT_ID}/recruitment:v4-corrected -f src/recruitment/Dockerfile .

echo "✅ Imágenes reconstruidas con TODAS las correcciones aplicadas"

docker push gcr.io/${PROJECT_ID}/onboarding:v11-corrected
docker push gcr.io/${PROJECT_ID}/partner-management:v4-corrected
docker push gcr.io/${PROJECT_ID}/recruitment:v4-corrected

echo "✅ Imágenes corregidas pusheadas a GCR"

kubectl set image deployment/onboarding onboarding=gcr.io/${PROJECT_ID}/onboarding:v11-corrected -n hexabuilders
kubectl set image deployment/recruitment recruitment=gcr.io/${PROJECT_ID}/recruitment:v4-corrected -n hexabuilders
kubectl set image deployment/partner-management partner-management=gcr.io/${PROJECT_ID}/partner-management:v4-corrected -n hexabuilders

echo "✅ Deployments actualizados con imágenes corregidas"

kubectl rollout status deployment/onboarding -n hexabuilders
kubectl rollout status deployment/recruitment -n hexabuilders
kubectl rollout status deployment/partner-management -n hexabuilders

echo "✅ Rollouts actualizados con imágenes corregidas"

---

## 🎯 URLs de Acceso

Una vez completado, tendrás acceso a:

- **Partner Management API**: `http://[EXTERNAL_IP]/api/v1/partners-query`
- **Health Checks**: `http://[EXTERNAL_IP]/health`
- **GCP Console**: https://console.cloud.google.com
- **Container Registry**: https://console.cloud.google.com/gcr

---

# Cambiar onboarding a NodePort
kubectl patch svc onboarding -n hexabuilders -p '{"spec":{"type":"NodePort"}}'

# Cambiar recruitment a NodePort  
kubectl patch svc recruitment -n hexabuilders -p '{"spec":{"type":"NodePort"}}'

# Cambiar campaign-management a NodePort
kubectl patch svc campaign-management -n hexabuilders -p '{"spec":{"type":"NodePort"}}'

# Cambiar partner-management a NodePort
kubectl patch svc partner-management -n hexabuilders -p '{"spec":{"type":"NodePort"}}'

echo "✅ Servicios configurados como NodePort"

# Ver IPs externas de los nodos
kubectl get nodes -o wide

# Ver puertos NodePort asignados
kubectl get svc -n hexabuilders

---

# Escalar todas las aplicaciones a 0 (pero mantener configuración)
kubectl scale deployment campaign-management onboarding partner-management postgres pulsar-standalone recruitment --replicas=0 -n hexabuilders

echo "✅ Todas las aplicaciones detenidas"

gcloud container clusters resize hexabuilders-cluster --num-nodes=0 --zone=us-central1-a --project=${PROJECT_ID}

echo "🛑 CLUSTER APAGADO"

---

# Volver a escalar a 4 nodos
gcloud container clusters resize hexabuilders-cluster --num-nodes=4 --zone=us-central1-a --project=${PROJECT_ID}

# Esperar a que nodos estén listos
kubectl get nodes -w

kubectl scale deployment campaign-management onboarding partner-management postgres pulsar-standalone recruitment --replicas=1 -n hexabuilders

echo "🚀 Todas las aplicaciones reactivadas"