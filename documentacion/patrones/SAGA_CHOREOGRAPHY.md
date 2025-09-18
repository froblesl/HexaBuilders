# Patrón Saga de Choreography - HexaBuilders

## 🎯 Visión General

El patrón Saga de Choreography implementa transacciones distribuidas de larga duración usando eventos para coordinar entre microservicios. Cada servicio maneja su propio estado y publica eventos para coordinar el flujo.

## 🏗️ Arquitectura

### **Características Principales**
- **Event-Driven**: Comunicación asíncrona mediante eventos
- **Desacoplado**: Cada servicio es independiente
- **Escalable**: Fácil agregar nuevos servicios
- **Resiliente**: Compensación automática en fallos
- **Observable**: Trazabilidad completa con correlation IDs

### **Flujo de la Saga**
```
Partner Registration → Contract Creation → Document Verification → Campaign Enablement → Recruitment Setup
```

## 📋 Caso de Uso: Partner Onboarding

### **Eventos de la Saga**

#### **Eventos de Progreso**
1. `PartnerOnboardingInitiated` - Inicia el proceso
2. `PartnerRegistrationCompleted` - Partner registrado
3. `ContractCreated` - Contrato creado
4. `DocumentsVerified` - Documentos verificados
5. `CampaignsEnabled` - Campañas habilitadas
6. `RecruitmentSetupCompleted` - Reclutamiento configurado
7. `PartnerOnboardingCompleted` - Proceso completado

#### **Eventos de Compensación**
1. `PartnerOnboardingFailed` - Proceso fallido
2. `CompensationRequested` - Solicitud de compensación
3. `CompensationCompleted` - Compensación completada

## 💻 Implementación

### **1. ChoreographySagaOrchestrator**
```python
class ChoreographySagaOrchestrator:
    """Orquestador de Saga basado en Choreography"""
    
    def __init__(self, event_dispatcher, saga_state_repository):
        self.event_dispatcher = event_dispatcher
        self.saga_state_repository = saga_state_repository
        self._register_event_handlers()
    
    async def start_partner_onboarding(self, partner_data, correlation_id):
        """Inicia el proceso de onboarding"""
        # Crear estado inicial
        # Publicar evento de inicio
        # Registrar handlers
```

### **2. Event Handlers**
```python
async def _handle_partner_registered(self, event):
    """Maneja partner registrado"""
    # Actualizar estado
    # Solicitar siguiente paso
    # Publicar evento de contrato

async def _handle_contract_created(self, event):
    """Maneja contrato creado"""
    # Actualizar estado
    # Solicitar verificación de documentos
    # Publicar evento de documentos
```

### **3. Compensación**
```python
async def _initiate_compensation(self, partner_id, failed_step, correlation_id):
    """Inicia compensación en orden inverso"""
    # Determinar pasos a compensar
    # Publicar eventos de compensación
    # Actualizar estado
```

## 🔧 API Endpoints

### **Iniciar Saga**
```bash
POST /sagas/partner-onboarding
{
  "partner_data": {
    "nombre": "TechSolutions Inc",
    "email": "contact@techsolutions.com",
    "telefono": "+1234567890",
    "tipo_partner": "EMPRESA",
    "preferred_contract_type": "PREMIUM"
  },
  "correlation_id": "corr-123-456"
}
```

### **Monitorear Estado**
```bash
GET /sagas/{partner_id}/status
```

### **Compensar Saga**
```bash
POST /sagas/{partner_id}/compensate
{
  "reason": "Manual compensation request"
}
```

## 📊 Estados de la Saga

### **ChoreographySagaStatus**
- `INITIATED` - Proceso iniciado
- `PARTNER_REGISTERED` - Partner registrado
- `CONTRACT_CREATED` - Contrato creado
- `DOCUMENTS_VERIFIED` - Documentos verificados
- `CAMPAIGNS_ENABLED` - Campañas habilitadas
- `RECRUITMENT_SETUP` - Reclutamiento configurado
- `COMPLETED` - Proceso completado
- `FAILED` - Proceso fallido
- `COMPENSATING` - En compensación
- `COMPENSATED` - Compensado

## 🛡️ Manejo de Errores

### **Compensación Automática**
- Se activa cuando un paso falla
- Ejecuta compensaciones en orden inverso
- Publica eventos de compensación
- Actualiza estado de la Saga

### **Retry y Timeout**
- Reintentos automáticos con backoff
- Timeouts configurables por paso
- Dead letter queue para eventos fallidos
- Logging detallado de errores

## 📈 Observabilidad

### **Métricas**
- Tiempo de procesamiento por paso
- Tasa de éxito/fallo
- Latencia de eventos
- Estado de compensaciones

### **Logging**
- Correlation IDs para trazabilidad
- Eventos de progreso
- Errores detallados
- Compensaciones registradas

### **Health Checks**
```bash
GET /sagas/health
```

## 🎯 Beneficios

1. **🔄 Desacoplamiento**: Servicios independientes
2. **⚡ Performance**: Procesamiento asíncrono
3. **🛡️ Resilencia**: Compensación automática
4. **📊 Observabilidad**: Trazabilidad completa
5. **🔧 Flexibilidad**: Fácil agregar pasos
6. **🌐 Escalabilidad**: Distribuido y escalable

## 🔍 Monitoreo

### **Dashboard de Sagas**
- Estado actual de todas las Sagas
- Pasos completados/fallidos
- Tiempo de procesamiento
- Métricas de compensación

### **Alertas**
- Sagas que fallan repetidamente
- Tiempo de procesamiento excesivo
- Errores de compensación
- Eventos perdidos

Esta implementación proporciona una base sólida para manejar transacciones distribuidas complejas de manera confiable y escalable usando el patrón Saga de Choreography.
