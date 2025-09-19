# BFF Web con GraphQL - HexaBuilders

## 🎯 Visión General

El BFF (Backend for Frontend) Web proporciona una API GraphQL optimizada para el frontend web, exponiendo la funcionalidad de Sagas de manera eficiente y fácil de usar.

## 🏗️ Arquitectura

### **Stack Tecnológico**
- **FastAPI**: Framework web asíncrono
- **Strawberry GraphQL**: Implementación GraphQL moderna
- **httpx**: Cliente HTTP asíncrono
- **Pydantic**: Validación de datos

### **Características**
- **GraphQL**: API flexible y eficiente
- **Type Safety**: Tipos fuertes con Strawberry
- **Async/Await**: Operaciones asíncronas
- **CORS**: Soporte para frontend cross-origin
- **Health Checks**: Monitoreo de dependencias

## 📋 Schema GraphQL

### **Tipos Principales**

#### **Enums**
```graphql
enum ChoreographySagaStatus {
  INITIATED
  PARTNER_REGISTERED
  CONTRACT_CREATED
  DOCUMENTS_VERIFIED
  CAMPAIGNS_ENABLED
  RECRUITMENT_SETUP
  COMPLETED
  FAILED
  COMPENSATING
  COMPENSATED
}

enum PartnerType {
  EMPRESA
  INDIVIDUAL
  FREELANCER
}

enum ContractType {
  BASIC
  STANDARD
  PREMIUM
  ENTERPRISE
}
```

#### **Tipos de Datos**
```graphql
type PartnerData {
  partnerId: String
  nombre: String!
  email: String!
  telefono: String!
  tipoPartner: PartnerType!
  preferredContractType: ContractType!
  requiredDocuments: [String!]!
  campaignPermissions: String
  recruitmentPreferences: String
}

type SagaStep {
  stepName: String!
  status: String!
  startedAt: DateTime
  completedAt: DateTime
  errorMessage: String
}

type SagaState {
  partnerId: String!
  sagaType: String!
  status: ChoreographySagaStatus!
  completedSteps: [String!]!
  failedSteps: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
  correlationId: String!
  steps: [SagaStep!]!
}

type SagaResponse {
  success: Boolean!
  message: String!
  partnerId: String
  sagaState: SagaState
  timestamp: DateTime!
}
```

## 🔍 Queries

### **1. Obtener Estado de Saga**
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

### **2. Health Check**
```graphql
query HealthCheck {
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

## 🔧 Mutations

### **1. Iniciar Onboarding de Partner**
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

**Input:**
```graphql
input PartnerOnboardingInput {
  partnerData: PartnerDataInput!
  correlationId: String
}

input PartnerDataInput {
  partnerId: String
  nombre: String!
  email: String!
  telefono: String!
  tipoPartner: PartnerType!
  preferredContractType: ContractType!
  requiredDocuments: [String!]!
  campaignPermissions: String
  recruitmentPreferences: String
}
```

### **2. Compensar Saga**
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

**Input:**
```graphql
input CompensationInput {
  reason: String!
}
```

## 🚀 Uso Práctico

### **1. Iniciar Onboarding**
```javascript
const START_ONBOARDING = gql`
  mutation StartPartnerOnboarding($input: PartnerOnboardingInput!) {
    startPartnerOnboarding(input: $input) {
      success
      message
      partnerId
      timestamp
    }
  }
`;

const variables = {
  input: {
    partnerData: {
      nombre: "TechSolutions Inc",
      email: "contact@techsolutions.com",
      telefono: "+1234567890",
      tipoPartner: "EMPRESA",
      preferredContractType: "PREMIUM",
      requiredDocuments: ["IDENTITY", "BUSINESS_REGISTRATION"]
    },
    correlationId: "web-123-456"
  }
};

const { data } = await client.mutate({
  mutation: START_ONBOARDING,
  variables
});
```

### **2. Monitorear Progreso**
```javascript
const GET_SAGA_STATUS = gql`
  query GetSagaStatus($partnerId: String!) {
    sagaStatus(partnerId: $partnerId) {
      status
      completedSteps
      failedSteps
      steps {
        stepName
        status
        startedAt
        completedAt
        errorMessage
      }
    }
  }
`;

// Polling cada 5 segundos
const pollSagaStatus = setInterval(async () => {
  const { data } = await client.query({
    query: GET_SAGA_STATUS,
    variables: { partnerId: "partner-123" }
  });
  
  if (data.sagaStatus.status === "COMPLETED" || 
      data.sagaStatus.status === "FAILED") {
    clearInterval(pollSagaStatus);
  }
}, 5000);
```

### **3. Compensar en Caso de Error**
```javascript
const COMPENSATE_SAGA = gql`
  mutation CompensateSaga($partnerId: String!, $input: CompensationInput!) {
    compensateSaga(partnerId: $partnerId, input: $input) {
      success
      message
      timestamp
    }
  }
`;

const { data } = await client.mutate({
  mutation: COMPENSATE_SAGA,
  variables: {
    partnerId: "partner-123",
    input: {
      reason: "User requested cancellation"
    }
  }
});
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

### **Docker**
```bash
# Construir imagen
docker build -f bff_web.Dockerfile -t hexabuilders-bff-web .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e SAGA_SERVICE_URL=http://partner-management:5000 \
  hexabuilders-bff-web
```

## 📊 Endpoints

### **GraphQL**
- **Endpoint**: `POST /api/v1/graphql`
- **Playground**: `GET /api/v1/graphql` (si está habilitado)

### **REST**
- **Health Check**: `GET /health`
- **Root**: `GET /`
- **Schema**: `GET /api/v1/schema`

## 🧪 Testing

### **Script de Prueba**
```bash
python test_bff_graphql.py
```

### **Ejemplo de Query**
```bash
curl -X POST http://localhost:8000/api/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { health { service status } }"
  }'
```

## 🎯 Beneficios

1. **🔄 Eficiencia**: Una sola request para múltiples datos
2. **📱 Frontend-Friendly**: API optimizada para web
3. **🛡️ Type Safety**: Validación de tipos en tiempo de compilación
4. **⚡ Performance**: Queries optimizadas y caching
5. **🔧 Flexibilidad**: Schema evolutivo sin breaking changes
6. **📊 Observabilidad**: Health checks y métricas integradas

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

Esta implementación proporciona una interfaz GraphQL moderna y eficiente para el frontend web, simplificando la integración con el sistema de Sagas de HexaBuilders.
