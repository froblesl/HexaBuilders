# Eventos de Integración - HexaBuilders Microservices

## 🎯 Propósito de los Integration Events

Los **Integration Events** son el mecanismo principal de comunicación asíncrona entre los bounded contexts (microservicios) de HexaBuilders. Estos eventos garantizan el desacoplamiento temporal y espacial entre servicios.

---

## 🏗️ Arquitectura de Integration Events

### **Características Principales**
- 🔄 **Asíncrono**: No bloquean el servicio emisor
- 🎯 **Idempotente**: Procesamiento seguro múltiples veces
- 📝 **Inmutable**: Una vez publicado, no se modifica
- 🏷️ **Versionado**: Evolución controlada de esquemas
- 📊 **Trazable**: Correlation ID para seguimiento end-to-end

### **Formato Cloud Events**
```json
{
  "specversion": "1.0",
  "type": "com.hexabuilders.partners.PartnerRegistrationCompleted",
  "source": "//partners/550e8400-e29b-41d4-a716-446655440000",
  "id": "A234-1234-1234",
  "time": "2025-01-15T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "partner_id": "550e8400-e29b-41d4-a716-446655440000",
    "business_name": "TechSolutions Inc",
    "email": "contact@techsolutions.com",
    "partner_type": "EMPRESA"
  },
  "correlationid": "CORR-123-456-789",
  "causationid": "CMD-987-654-321"
}
```

---

## 📡 Topics de Apache Pulsar

### **Estructura de Topics**
```
persistent://hexabuilders/{service}/{event-category}
```

#### **Partner Management Service**
```
persistent://hexabuilders/partner-management/partner-registration
persistent://hexabuilders/partner-management/partner-validation
persistent://hexabuilders/partner-management/recruitment-requests
persistent://hexabuilders/partner-management/metrics-snapshots
```

#### **Onboarding Service**
```
persistent://hexabuilders/onboarding/contract-signed
persistent://hexabuilders/onboarding/contract-activated
persistent://hexabuilders/onboarding/employment-contract
```

#### **Recruitment Service**
```
persistent://hexabuilders/recruitment/candidate-matched
persistent://hexabuilders/recruitment/candidate-hired
persistent://hexabuilders/recruitment/recruitment-completed
```

#### **Campaign Management Service**
```
persistent://hexabuilders/campaign-management/performance-report
persistent://hexabuilders/campaign-management/budget-alerts
persistent://hexabuilders/campaign-management/campaign-insights
persistent://hexabuilders/campaign-management/optimization-suggestions
```

---

## 🔄 Matriz de Comunicación Inter-Servicios

| Evento | Servicio Origen | Servicio Destino | Propósito | Criticidad |
|--------|----------------|------------------|-----------|------------|
| `PartnerRegistrationCompleted` | Partner Mgmt | Onboarding | Iniciar proceso contractual | 🔴 Alta |
| `PartnerValidationCompleted` | Partner Mgmt | Campaign Mgmt | Habilitar campañas | 🟡 Media |
| `RecruitmentRequested` | Partner Mgmt | Recruitment | Buscar candidatos | 🟡 Media |
| `ContractSigned` | Onboarding | Partner Mgmt | Actualizar estado partner | 🔴 Alta |
| `ContractActivated` | Onboarding | Campaign Mgmt | Habilitar funcionalidades | 🔴 Alta |
| `CandidateMatched` | Recruitment | Partner Mgmt | Notificar matches | 🟡 Media |
| `CandidateHired` | Recruitment | Partner Mgmt + Onboarding | Actualizar métricas + Contrato laboral | 🔴 Alta |
| `CampaignPerformanceReport` | Campaign Mgmt | Partner Mgmt | Actualizar métricas partner | 🟡 Media |
| `BudgetAlert` | Campaign Mgmt | Partner Mgmt | Alertas presupuestarias | 🟠 Alta |

---

## 📋 Detalle de Integration Events

### **1. Partner Management → Onboarding**

#### **PartnerRegistrationCompleted**
```python
class PartnerRegistrationCompleted(IntegrationEvent):
    """
    Disparado cuando un partner completa el registro inicial
    y está listo para el proceso de onboarding contractual.
    """
    
    # Datos del evento
    partner_id: str              # UUID del partner
    business_name: str           # Nombre comercial
    email: str                   # Email de contacto principal
    partner_type: str            # INDIVIDUAL, EMPRESA, STARTUP
    registration_data: dict      # Datos completos de registro
    validation_status: str       # PENDING, PARTIAL, COMPLETE
    preferred_contract_type: str # STANDARD, PREMIUM, ENTERPRISE
    
    # Metadatos
    registration_source: str     # WEB, API, REFERRAL
    registration_timestamp: str  # ISO 8601 timestamp
    
    # Topic: partner-management/partner-registration
    # Subscriber: onboarding-service
    # Idempotency Key: partner_id
```

**Procesamiento en Onboarding**:
```python
@event_handler('partner-management/partner-registration')
async def on_partner_registration_completed(event: PartnerRegistrationCompleted):
    # 1. Verificar idempotencia
    if await self.contract_repo.exists_by_partner(event.partner_id):
        logger.info(f"Contract already exists for partner {event.partner_id}")
        return
    
    # 2. Determinar tipo de contrato
    contract_template = await self.template_service.get_template(
        event.preferred_contract_type, 
        event.partner_type
    )
    
    # 3. Crear borrador de contrato
    command = CreateContract(
        partner_id=event.partner_id,
        contract_type=event.preferred_contract_type,
        template_id=contract_template.id,
        initial_data=event.registration_data
    )
    
    await self.command_bus.dispatch(command)
```

---

### **2. Onboarding → Multiple Services**

#### **ContractActivated**
```python
class ContractActivated(IntegrationEvent):
    """
    Disparado cuando un contrato es firmado y activado,
    habilitando funcionalidades en otros servicios.
    """
    
    # Datos del contrato
    contract_id: str             # UUID del contrato
    partner_id: str              # UUID del partner
    contract_type: str           # STANDARD, PREMIUM, ENTERPRISE
    effective_date: str          # Fecha de vigencia
    expiration_date: str         # Fecha de vencimiento
    
    # Permisos y límites
    campaign_permissions: list   # Permisos de campaña otorgados
    budget_limits: dict          # Límites presupuestarios
    feature_flags: dict          # Funcionalidades habilitadas
    sla_terms: dict              # Términos de SLA acordados
    
    # Datos financieros
    commission_structure: dict   # Estructura de comisiones
    payment_terms: dict          # Términos de pago
    
    # Topics: 
    # - onboarding/contract-activated → campaign-management
    # - onboarding/contract-activated → partner-management
```

**Procesamiento en Campaign Management**:
```python
@event_handler('onboarding/contract-activated')
async def on_contract_activated(event: ContractActivated):
    # 1. Habilitar creación de campañas
    command = EnableCampaignCreation(
        partner_id=event.partner_id,
        permissions=event.campaign_permissions,
        budget_limits=event.budget_limits
    )
    
    # 2. Configurar límites y restricciones
    await self.partner_config_service.update_permissions(
        partner_id=event.partner_id,
        permissions=event.campaign_permissions,
        limits=event.budget_limits
    )
```

**Procesamiento en Partner Management**:
```python
@event_handler('onboarding/contract-activated')
async def on_contract_activated(event: ContractActivated):
    # 1. Actualizar estado del partner
    command = UpdatePartnerStatus(
        partner_id=event.partner_id,
        new_status=PartnerStatus.VALIDATED,
        contract_id=event.contract_id
    )
    
    # 2. Registrar métricas contractuales
    await self.metrics_service.record_contract_activation(
        partner_id=event.partner_id,
        contract_data=event
    )
```

---

### **3. Partner Management → Recruitment**

#### **RecruitmentRequested**
```python
class RecruitmentRequested(IntegrationEvent):
    """
    Disparado cuando un partner solicita servicios de reclutamiento.
    """
    
    # Identificación
    request_id: str              # UUID de la solicitud
    partner_id: str              # UUID del partner solicitante
    
    # Requisitos del trabajo
    job_requirements: dict       # Requisitos detallados
    required_skills: list        # Skills técnicos requeridos
    experience_level: str        # JUNIOR, MID, SENIOR, EXPERT
    job_type: str               # FULL_TIME, PART_TIME, CONTRACT
    remote_work_allowed: bool    # Trabajo remoto permitido
    location_preferences: list   # Ubicaciones preferidas
    
    # Presupuesto y términos
    salary_range: dict          # Rango salarial
    budget_range: dict          # Presupuesto para reclutamiento
    hiring_timeline: dict       # Timeline de contratación
    urgency_level: str          # LOW, NORMAL, HIGH, URGENT
    
    # Preferencias
    candidate_sources: list     # INTERNAL, EXTERNAL, REFERRALS
    screening_criteria: dict    # Criterios de preselección
    
    # Topic: partner-management/recruitment-requests
    # Subscriber: recruitment-service
```

**Procesamiento en Recruitment**:
```python
@event_handler('partner-management/recruitment-requests')
async def on_recruitment_requested(event: RecruitmentRequested):
    # 1. Crear trabajo en el sistema
    command = CreateJob(
        partner_id=event.partner_id,
        job_requirements=event.job_requirements,
        budget_info=event.salary_range
    )
    
    job_id = await self.command_bus.dispatch(command)
    
    # 2. Iniciar proceso de matching
    matching_command = StartMatching(
        job_id=job_id,
        required_skills=event.required_skills,
        experience_level=event.experience_level,
        urgency=event.urgency_level
    )
    
    await self.command_bus.dispatch(matching_command)
```

---

### **4. Recruitment → Multiple Services**

#### **CandidateHired**
```python
class CandidateHired(IntegrationEvent):
    """
    Disparado cuando un candidato es contratado exitosamente.
    """
    
    # Identificación
    hiring_id: str              # UUID del proceso de contratación
    partner_id: str             # UUID del partner empleador
    candidate_id: str           # UUID del candidato
    job_id: str                 # UUID del trabajo
    
    # Detalles del empleo
    employment_details: dict    # Detalles completos del empleo
    job_title: str             # Título del puesto
    department: str            # Departamento
    start_date: str            # Fecha de inicio
    employment_type: str       # PERMANENT, CONTRACT, INTERNSHIP
    
    # Términos financieros
    agreed_salary: float       # Salario acordado
    currency: str              # Moneda
    benefits_package: dict     # Paquete de beneficios
    
    # Proceso de contratación
    hiring_process_metrics: dict   # Métricas del proceso
    time_to_hire: int             # Días desde solicitud hasta contratación
    recruitment_cost: float       # Costo del reclutamiento
    
    # Topics:
    # - recruitment/candidate-hired → partner-management
    # - recruitment/candidate-hired → onboarding
```

**Procesamiento en Partner Management**:
```python
@event_handler('recruitment/candidate-hired')
async def on_candidate_hired(event: CandidateHired):
    # 1. Actualizar métricas del partner
    command = UpdatePartnerMetrics(
        partner_id=event.partner_id,
        metric_updates={
            'successful_hires': 1,
            'recruitment_cost': event.recruitment_cost,
            'average_time_to_hire': event.time_to_hire
        }
    )
    
    await self.command_bus.dispatch(command)
```

**Procesamiento en Onboarding**:
```python
@event_handler('recruitment/candidate-hired')
async def on_candidate_hired(event: CandidateHired):
    # 1. Iniciar proceso de contrato laboral
    command = CreateEmploymentContract(
        partner_id=event.partner_id,
        candidate_id=event.candidate_id,
        employment_terms=event.employment_details
    )
    
    await self.command_bus.dispatch(command)
```

---

### **5. Campaign Management → Partner Management**

#### **CampaignPerformanceReport**
```python
class CampaignPerformanceReport(IntegrationEvent):
    """
    Reporte periódico de rendimiento de campañas.
    """
    
    # Identificación
    report_id: str              # UUID del reporte
    campaign_id: str            # UUID de la campaña
    partner_id: str             # UUID del partner
    reporting_period: dict      # Período del reporte
    
    # Métricas de rendimiento
    performance_summary: dict   # Resumen de rendimiento
    kpi_achievements: dict      # Logros de KPIs
    roi_metrics: dict          # Métricas de ROI
    engagement_metrics: dict   # Métricas de engagement
    
    # Análisis comparativo
    period_comparison: dict     # Comparación con período anterior
    benchmark_comparison: dict  # Comparación con benchmarks
    trend_analysis: dict       # Análisis de tendencias
    
    # Insights y recomendaciones
    performance_insights: list  # Insights automatizados
    optimization_suggestions: list # Sugerencias de optimización
    risk_indicators: list      # Indicadores de riesgo
    
    # Topic: campaign-management/performance-report
    # Subscribers: partner-management, analytics-service
```

#### **BudgetAlert**
```python
class BudgetAlert(IntegrationEvent):
    """
    Alerta cuando se alcanzan umbrales presupuestarios.
    """
    
    # Identificación
    alert_id: str               # UUID de la alerta
    campaign_id: str            # UUID de la campaña
    partner_id: str             # UUID del partner
    
    # Datos presupuestarios
    budget_status: dict         # Estado actual del presupuesto
    alert_type: str            # WARNING, CRITICAL, EXHAUSTED
    threshold_reached: float   # Porcentaje del umbral alcanzado
    current_spend: float       # Gasto actual
    budget_limit: float        # Límite presupuestario
    
    # Proyecciones
    projected_spend: float     # Gasto proyectado
    days_remaining: int        # Días restantes de la campaña
    burn_rate: float          # Tasa de quemado diaria
    
    # Acciones recomendadas
    recommended_actions: list  # Acciones sugeridas
    automatic_actions_taken: list # Acciones automáticas ya tomadas
    
    # Topics:
    # - campaign-management/budget-alerts → partner-management
    # - campaign-management/budget-alerts → notifications
```

---

## 🔧 Configuración de Suscripciones

### **Subscription Model**
```python
# Configuración de suscripción shared para alta disponibilidad
SUBSCRIPTION_CONFIG = {
    'subscription_name': 'onboarding-service-subscription',
    'subscription_type': pulsar.ConsumerType.Shared,
    'subscription_initial_position': pulsar.InitialPosition.Earliest,
    'negative_ack_redelivery_delay_ms': 1000,
    'ack_timeout_ms': 30000,
    'max_redeliver_count': 3,
    'dead_letter_topic': 'hexabuilders/onboarding/dead-letters'
}
```

### **Error Handling & Retry**
```python
class IntegrationEventHandler:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(TransientException)
    )
    async def handle_event(self, event: IntegrationEvent):
        try:
            await self.process_event(event)
            await self.ack_event(event)
        except PermanentException:
            await self.send_to_dead_letter_queue(event)
        except Exception as e:
            logger.error(f"Unexpected error processing event: {e}")
            raise TransientException(str(e))
```

---

## 📊 Monitoreo y Observabilidad

### **Métricas de Integration Events**
```python
class EventMetrics:
    # Métricas de publicación
    events_published_total: Counter
    events_published_by_type: Counter
    event_publish_duration: Histogram
    event_publish_errors: Counter
    
    # Métricas de consumo
    events_consumed_total: Counter
    events_consumed_by_type: Counter
    event_processing_duration: Histogram
    event_processing_errors: Counter
    
    # Métricas de lag
    consumer_lag: Gauge
    dead_letter_queue_size: Gauge
```

### **Health Checks**
```python
@app.route('/health/events')
async def events_health_check():
    health_status = {
        'pulsar_connection': await check_pulsar_connection(),
        'consumer_lag': await get_consumer_lag(),
        'error_rate': await get_error_rate(),
        'dead_letter_queue_size': await get_dlq_size()
    }
    
    overall_healthy = all(health_status.values())
    status_code = 200 if overall_healthy else 503
    
    return jsonify(health_status), status_code
```

---

Los Integration Events son la columna vertebral de la comunicación entre microservicios en HexaBuilders, proporcionando un mecanismo robusto, escalable y observable para la coordinación de procesos de negocio distribuidos.