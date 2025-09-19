# BFF Web con GraphQL - HexaBuilders

## 🎯 Descripción

Backend for Frontend (BFF) que expone la funcionalidad de Sagas de HexaBuilders a través de una API GraphQL moderna y eficiente para el frontend web.

## 🚀 Inicio Rápido

### **1. Instalación de Dependencias**
```bash
pip install -r requirements-bff.txt
```

### **2. Ejecutar en Desarrollo**
```bash
python run_bff_web.py
```

### **3. Ejecutar con Docker**
```bash
# Construir imagen
docker build -f bff_web.Dockerfile -t hexabuilders-bff-web .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e SAGA_SERVICE_URL=http://partner-management:5000 \
  hexabuilders-bff-web
```

### **4. Ejecutar con Docker Compose**
```bash
# Solo BFF
docker-compose --profile bff up bff-web

# BFF + Servicios
docker-compose --profile full up
```

## 📊 Endpoints

- **GraphQL**: `http://localhost:8000/api/v1/graphql`
- **Health Check**: `http://localhost:8000/health`
- **Schema**: `http://localhost:8000/api/v1/schema`

## 🧪 Testing

### **Script de Prueba**
```bash
python test_bff_graphql.py
```

### **Query de Ejemplo**
```bash
curl -X POST http://localhost:8000/api/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { health { service status } }"
  }'
```

## 🔧 Configuración

### **Variables de Entorno**
```bash
# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Servicios
SAGA_SERVICE_URL=http://partner-management:5000
SAGA_SERVICE_TIMEOUT=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging
LOG_LEVEL=INFO
```

## 📋 Queries GraphQL

### **Health Check**
```graphql
query {
  health {
    service
    status
    pattern
    sagaTypes
    eventDispatcher
    timestamp
  }
}
```

### **Estado de Saga**
```graphql
query GetSagaStatus($partnerId: String!) {
  sagaStatus(partnerId: $partnerId) {
    partnerId
    sagaType
    status
    completedSteps
    failedSteps
    createdAt
    updatedAt
    correlationId
    steps {
      stepName
      status
      startedAt
      completedAt
      errorMessage
    }
  }
}
```

## 🔧 Mutations GraphQL

### **Iniciar Onboarding**
```graphql
mutation StartPartnerOnboarding($input: PartnerOnboardingInput!) {
  startPartnerOnboarding(input: $input) {
    success
    message
    partnerId
    timestamp
  }
}
```

### **Compensar Saga**
```graphql
mutation CompensateSaga($partnerId: String!, $input: CompensationInput!) {
  compensateSaga(partnerId: $partnerId, input: $input) {
    success
    message
    partnerId
    timestamp
  }
}
```

## 🎯 Características

- ✅ **GraphQL**: API flexible y eficiente
- ✅ **Type Safety**: Tipos fuertes con Strawberry
- ✅ **Async/Await**: Operaciones asíncronas
- ✅ **CORS**: Soporte para frontend cross-origin
- ✅ **Health Checks**: Monitoreo de dependencias
- ✅ **Docker**: Contenedorización completa
- ✅ **Testing**: Scripts de prueba incluidos

## 📚 Documentación

- [BFF Web GraphQL](./documentacion/bff/BFF_WEB_GRAPHQL.md)
- [Saga Choreography](./documentacion/patrones/SAGA_CHOREOGRAPHY.md)

## 🔍 Monitoreo

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Métricas**
- Tiempo de respuesta de queries
- Tasa de éxito de mutations
- Estado de dependencias
- Uso de memoria y CPU

## 🛠️ Desarrollo

### **Estructura del Proyecto**
```
src/bff_web/
├── __init__.py
├── app.py              # Aplicación FastAPI
├── schema.py           # Schema GraphQL
├── resolvers.py        # Resolvers GraphQL
├── saga_client.py      # Cliente para servicio de Saga
└── config.py           # Configuración
```

### **Agregar Nuevas Queries/Mutations**
1. Definir tipos en `schema.py`
2. Implementar resolvers en `resolvers.py`
3. Agregar métodos al cliente en `saga_client.py`
4. Actualizar tests en `test_bff_graphql.py`

## 🚀 Despliegue

### **Producción**
```bash
# Construir imagen
docker build -f bff_web.Dockerfile -t hexabuilders-bff-web:latest .

# Ejecutar en producción
docker run -d \
  --name bff-web \
  -p 8000:8000 \
  -e SAGA_SERVICE_URL=http://partner-management:5000 \
  -e DEBUG=false \
  hexabuilders-bff-web:latest
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bff-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bff-web
  template:
    metadata:
      labels:
        app: bff-web
    spec:
      containers:
      - name: bff-web
        image: hexabuilders-bff-web:latest
        ports:
        - containerPort: 8000
        env:
        - name: SAGA_SERVICE_URL
          value: "http://partner-management:5000"
```

Este BFF proporciona una interfaz GraphQL moderna y eficiente para el frontend web, simplificando la integración con el sistema de Sagas de HexaBuilders.
