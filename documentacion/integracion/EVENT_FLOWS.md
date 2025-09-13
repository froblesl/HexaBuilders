# Flujos de Eventos por Escenario - HexaBuilders

## 🎯 Visión General

Este documento describe los flujos completos de eventos para los principales escenarios de negocio en HexaBuilders, mostrando la secuencia temporal y las interacciones entre microservicios.

---

## 🔄 Escenario 1: Onboarding Completo de Partner

### **Descripción**
Un nuevo partner se registra en HexaBuilders y completa todo el proceso hasta poder crear campañas.

### **Actores**
- **Partner**: Nuevo usuario empresarial
- **Partner Management Service**: Gestión de partners
- **Onboarding Service**: Proceso contractual
- **Campaign Management Service**: Gestión de campañas
- **Notifications Service**: Notificaciones

### **Flujo Temporal Detallado**

```mermaid
sequenceDiagram
    participant P as Partner
    participant PM as Partner Management
    participant OB as Onboarding
    participant CM as Campaign Management
    participant NT as Notifications

    Note over P, NT: Fase 1: Registro Inicial
    P->>PM: POST /partners (registro)
    PM->>PM: Validar datos
    PM->>PM: Crear partner (DRAFT)
    PM->>NT: PartnerCreated (domain event)
    PM->>P: 202 Accepted

    Note over P, NT: Fase 2: Validación Inicial
    PM->>PM: Procesar validaciones
    PM->>PM: Validar email/teléfono
    PM->>PM: Actualizar estado (PENDING_VALIDATION)
    
    Note over P, NT: Fase 3: Completar Registro
    P->>PM: PUT /partners/{id}/validation
    PM->>PM: Completar validación
    PM->>PM: Cambiar estado (REGISTERED)
    
    Note over P, NT: Fase 4: Iniciar Onboarding
    PM->>OB: PartnerRegistrationCompleted (integration event)
    OB->>OB: Recibir evento
    OB->>OB: Crear borrador contrato
    OB->>OB: Determinar tipo contrato
    OB->>NT: ContractCreated (notification)
    OB->>P: Email con link de contrato

    Note over P, NT: Fase 5: Proceso Contractual
    P->>OB: Revisar términos contrato
    P->>OB: POST /contracts/{id}/negotiate
    OB->>OB: Procesar negociación
    OB->>OB: Aplicar términos acordados
    
    Note over P, NT: Fase 6: Validación Legal
    OB->>OB: Solicitar validación legal
    OB->>OB: Validar compliance
    OB->>OB: Aprobar términos legales
    
    Note over P, NT: Fase 7: Firma Digital
    P->>OB: POST /contracts/{id}/sign
    OB->>OB: Procesar firma digital
    OB->>OB: Validar autenticidad
    OB->>OB: Completar firma
    
    Note over P, NT: Fase 8: Activación de Contrato
    OB->>OB: Activar contrato
    OB->>PM: ContractSigned (integration event)
    OB->>CM: ContractActivated (integration event)
    OB->>NT: ContractActivated (notification)
    
    Note over P, NT: Fase 9: Actualización de Estados
    PM->>PM: Recibir ContractSigned
    PM->>PM: Actualizar estado (VALIDATED)
    PM->>PM: Registrar datos contractuales
    
    CM->>CM: Recibir ContractActivated
    CM->>CM: Habilitar funcionalidades
    CM->>CM: Configurar límites presupuestarios
    CM->>CM: Configurar permisos de campaña
    
    NT->>P: Email de bienvenida
    NT->>P: Guía de primeros pasos
```

### **Eventos Intercambiados**

| Orden | Evento | Tipo | Origen | Destino | Payload Principal |
|-------|--------|------|--------|---------|-------------------|
| 1 | `PartnerCreated` | Domain | Partner Management | Internal | `{partner_id, basic_info}` |
| 2 | `PartnerRegistrationCompleted` | Integration | Partner Management | Onboarding | `{partner_id, registration_data, partner_type}` |
| 3 | `ContractCreated` | Domain | Onboarding | Internal | `{contract_id, partner_id, terms}` |
| 4 | `ContractSigned` | Integration | Onboarding | Partner Management | `{contract_id, partner_id, signed_terms}` |
| 5 | `ContractActivated` | Integration | Onboarding | Campaign Management | `{contract_id, partner_id, permissions}` |

### **Métricas y SLAs**
- **Tiempo total estimado**: 2-5 días laborales
- **Tiempo crítico**: Registro a contrato creado < 30 minutos
- **SLA eventos críticos**: < 5 segundos
- **Tasa de éxito esperada**: > 85%

---

## 👥 Escenario 2: Proceso de Reclutamiento Completo

### **Descripción**
Un partner solicita reclutamiento de candidatos, se ejecuta el matching y se completa la contratación.

### **Flujo Temporal Detallado**

```mermaid
sequenceDiagram
    participant P as Partner
    participant PM as Partner Management
    participant RC as Recruitment
    participant OB as Onboarding
    participant NT as Notifications

    Note over P, NT: Fase 1: Solicitud de Reclutamiento
    P->>PM: POST /recruitment/request
    PM->>PM: Validar permisos partner
    PM->>PM: Crear solicitud reclutamiento
    PM->>RC: RecruitmentRequested (integration event)
    PM->>P: 202 Accepted

    Note over P, NT: Fase 2: Creación de Trabajo
    RC->>RC: Recibir RecruitmentRequested
    RC->>RC: Crear trabajo en sistema
    RC->>RC: Configurar requisitos
    RC->>NT: JobCreated (notification)

    Note over P, NT: Fase 3: Proceso de Matching
    RC->>RC: Ejecutar algoritmos matching
    RC->>RC: Buscar candidatos compatibles
    RC->>RC: Calcular puntuaciones match
    RC->>RC: Ranking de candidatos
    
    loop Para cada candidato top
        RC->>RC: Validar disponibilidad
        RC->>PM: CandidateMatched (integration event)
        PM->>PM: Registrar match disponible
        PM->>NT: NewCandidateMatch (notification)
        NT->>P: Notificación nuevo match
    end

    Note over P, NT: Fase 4: Proceso de Entrevistas
    P->>RC: POST /interviews/schedule
    RC->>RC: Programar entrevista
    RC->>NT: InterviewScheduled (notification)
    NT->>P: Confirmación entrevista
    NT->>Candidate: Invitación entrevista
    
    RC->>RC: Completar entrevista
    RC->>RC: Procesar feedback
    RC->>RC: Evaluar candidato

    Note over P, NT: Fase 5: Decisión de Contratación
    P->>RC: POST /hiring/decision
    RC->>RC: Procesar decisión
    RC->>RC: Registrar contratación
    
    Note over P, NT: Fase 6: Notificación de Contratación
    RC->>PM: CandidateHired (integration event)
    RC->>OB: CandidateHired (integration event)
    RC->>NT: CandidateHired (notification)
    
    Note over P, NT: Fase 7: Actualización de Métricas
    PM->>PM: Recibir CandidateHired
    PM->>PM: Actualizar métricas partner
    PM->>PM: Incrementar contrataciones exitosas
    
    Note over P, NT: Fase 8: Proceso Contractual Laboral
    OB->>OB: Recibir CandidateHired
    OB->>OB: Crear contrato laboral
    OB->>OB: Procesar términos empleo
    OB->>NT: EmploymentContractCreated
    
    NT->>P: Confirmación contratación
    NT->>Candidate: Bienvenida y contrato
```

### **Eventos Intercambiados**

| Orden | Evento | Tipo | Origen | Destino | Payload Principal |
|-------|--------|------|--------|---------|-------------------|
| 1 | `RecruitmentRequested` | Integration | Partner Management | Recruitment | `{partner_id, job_requirements, urgency}` |
| 2 | `CandidateMatched` | Integration | Recruitment | Partner Management | `{match_id, candidate_id, match_score}` |
| 3 | `InterviewScheduled` | Domain | Recruitment | Internal | `{interview_id, candidate_id, datetime}` |
| 4 | `CandidateHired` | Integration | Recruitment | Partner Management, Onboarding | `{hiring_id, partner_id, candidate_id}` |

### **Métricas y SLAs**
- **Tiempo total estimado**: 1-3 semanas
- **Tiempo de matching**: < 24 horas
- **SLA notificaciones**: < 2 segundos
- **Tasa de éxito esperada**: > 70%

---

## 📊 Escenario 3: Ciclo de Vida de Campaña

### **Descripción**
Un partner validated crea, lanza y gestiona una campaña completa con optimización automática.

### **Flujo Temporal Detallado**

```mermaid
sequenceDiagram
    participant P as Partner
    participant CM as Campaign Management
    participant PM as Partner Management
    participant NT as Notifications
    participant AD as Ad Platforms

    Note over P, AD: Fase 1: Creación de Campaña
    P->>CM: POST /campaigns
    CM->>PM: GET /partners/{id}/permissions (sync API)
    PM->>CM: Partner permissions
    CM->>CM: Validar permisos creación
    CM->>CM: Crear campaña (DRAFT)
    CM->>P: 201 Created

    Note over P, AD: Fase 2: Configuración Avanzada
    P->>CM: PUT /campaigns/{id}/targeting
    CM->>CM: Configurar audiencias
    CM->>CM: Estimar alcance
    
    P->>CM: PUT /campaigns/{id}/budget
    CM->>CM: Asignar presupuesto
    CM->>CM: Configurar límites
    
    P->>CM: PUT /campaigns/{id}/creative
    CM->>CM: Subir creativos
    CM->>CM: Validar formatos

    Note over P, AD: Fase 3: Lanzamiento
    P->>CM: POST /campaigns/{id}/launch
    CM->>CM: Validar precondiciones
    CM->>CM: Activar campaña
    CM->>AD: Enviar a plataformas publicitarias
    CM->>NT: CampaignLaunched (notification)
    NT->>P: Confirmación lanzamiento

    Note over P, AD: Fase 4: Monitoreo en Tiempo Real
    loop Cada minuto
        AD->>CM: Métricas tiempo real
        CM->>CM: Procesar métricas
        CM->>CM: Actualizar dashboard
        CM->>P: WebSocket update
        
        CM->>CM: Verificar umbrales
        alt Umbral alcanzado
            CM->>PM: MetricThresholdReached (integration event)
            CM->>NT: CampaignAlert (notification)
            NT->>P: Alerta en tiempo real
        end
    end

    Note over P, AD: Fase 5: Optimización Automática
    CM->>CM: Detectar oportunidades optimización
    CM->>CM: Aplicar algoritmos avanzados para recomendaciones
    
    alt Optimización automática elegible
        CM->>CM: Aplicar optimización
        CM->>AD: Actualizar configuración
        CM->>NT: CampaignOptimized (notification)
        NT->>P: Notificación optimización
    else Optimización manual requerida
        CM->>NT: OptimizationSuggestion (notification)
        NT->>P: Sugerencia de optimización
    end

    Note over P, AD: Fase 6: Gestión Presupuestaria
    CM->>CM: Monitorear gasto
    CM->>CM: Calcular burn rate
    
    alt Presupuesto crítico
        CM->>PM: BudgetAlert (integration event)
        CM->>NT: BudgetAlert (notification)
        NT->>P: Alerta presupuestaria
        
        CM->>CM: Auto-pausar si configurado
        CM->>AD: Pausar campaña
    end

    Note over P, AD: Fase 7: Reporting Periódico
    CM->>CM: Generar reporte diario
    CM->>PM: CampaignPerformanceReport (integration event)
    CM->>NT: DailyReport (notification)
    
    PM->>PM: Actualizar métricas partner
    NT->>P: Reporte diario por email

    Note over P, AD: Fase 8: Finalización
    alt Campaña completada
        CM->>CM: Finalizar por cronograma
    else Pausada manualmente
        P->>CM: POST /campaigns/{id}/pause
        CM->>CM: Pausar campaña
    end
    
    CM->>CM: Generar métricas finales
    CM->>AD: Detener en plataformas
    CM->>PM: CampaignCompleted (integration event)
    CM->>NT: CampaignCompleted (notification)
    
    PM->>PM: Actualizar métricas finales
    NT->>P: Reporte final campaña
```

### **Eventos Intercambiados**

| Orden | Evento | Tipo | Origen | Destino | Payload Principal |
|-------|--------|------|--------|---------|-------------------|
| 1 | `CampaignCreated` | Domain | Campaign Management | Internal | `{campaign_id, partner_id, goals}` |
| 2 | `CampaignLaunched` | Domain | Campaign Management | Internal | `{campaign_id, launch_config}` |
| 3 | `MetricUpdated` | Domain | Campaign Management | Internal | `{campaign_id, metrics, timestamp}` |
| 4 | `BudgetAlert` | Integration | Campaign Management | Partner Management | `{campaign_id, budget_status, alert_level}` |
| 5 | `CampaignPerformanceReport` | Integration | Campaign Management | Partner Management | `{campaign_id, performance_data, period}` |
| 6 | `CampaignCompleted` | Integration | Campaign Management | Partner Management | `{campaign_id, final_metrics, success_indicators}` |

### **Métricas y SLAs**
- **Tiempo de lanzamiento**: < 5 minutos desde solicitud
- **Latencia métricas tiempo real**: < 30 segundos
- **SLA alertas críticas**: < 10 segundos
- **Disponibilidad dashboard**: > 99.5%

---

## 🔄 Escenario 4: Renovación de Contrato

### **Descripción**
Un contrato existente se acerca a su vencimiento y se ejecuta el proceso de renovación.

### **Flujo Temporal Detallado**

```mermaid
sequenceDiagram
    participant System as System Scheduler
    participant OB as Onboarding
    participant PM as Partner Management
    participant CM as Campaign Management
    participant NT as Notifications
    participant P as Partner

    Note over System, P: Fase 1: Detección de Vencimiento
    System->>OB: Scheduled job (diario)
    OB->>OB: Verificar contratos por vencer
    OB->>OB: Identificar contratos 30 días
    
    loop Para cada contrato por vencer
        OB->>PM: ContractExpirationApproaching (integration event)
        OB->>NT: ContractRenewalReminder (notification)
        NT->>P: Email recordatorio renovación
    end

    Note over System, P: Fase 2: Análisis de Renovación
    PM->>PM: Analizar performance partner
    PM->>PM: Calcular métricas período
    PM->>CM: GET /campaigns/partner/{id}/summary (sync API)
    CM->>PM: Resumen performance campañas
    
    PM->>PM: Generar recomendación renovación
    PM->>OB: PartnerRenewalRecommendation (integration event)

    Note over System, P: Fase 3: Proceso de Renovación
    OB->>OB: Crear propuesta renovación
    OB->>OB: Ajustar términos basado en performance
    OB->>NT: RenewalProposalReady (notification)
    NT->>P: Propuesta de renovación

    P->>OB: POST /contracts/{id}/renew
    OB->>OB: Procesar solicitud renovación
    
    alt Renovación automática (términos iguales)
        OB->>OB: Renovar automáticamente
        OB->>PM: ContractRenewed (integration event)
        OB->>NT: ContractRenewed (notification)
    else Negociación requerida
        OB->>OB: Iniciar proceso negociación
        Note over OB, P: Proceso similar a onboarding inicial
    end

    Note over System, P: Fase 4: Activación Nueva Vigencia
    OB->>CM: ContractRenewed (integration event)
    OB->>NT: ContractRenewed (notification)
    
    CM->>CM: Actualizar permisos y límites
    PM->>PM: Actualizar datos contractuales
    NT->>P: Confirmación renovación
```

### **Eventos Intercambiados**

| Orden | Evento | Tipo | Origen | Destino | Payload Principal |
|-------|--------|------|--------|---------|-------------------|
| 1 | `ContractExpirationApproaching` | Integration | Onboarding | Partner Management | `{contract_id, expiration_date, days_remaining}` |
| 2 | `PartnerRenewalRecommendation` | Integration | Partner Management | Onboarding | `{partner_id, performance_data, recommendation}` |
| 3 | `ContractRenewed` | Integration | Onboarding | Partner Management, Campaign Management | `{contract_id, new_terms, effective_period}` |

---

## 📊 Métricas Globales de Flujos

### **Tiempos de Procesamiento Objetivo**

| Escenario | Tiempo Total | Tiempo Crítico | SLA Eventos |
|-----------|--------------|----------------|-------------|
| **Onboarding Completo** | 2-5 días | < 30 min | < 5s |
| **Reclutamiento** | 1-3 semanas | < 24h | < 2s |
| **Ciclo Campaña** | Variable | < 5 min | < 30s |
| **Renovación Contrato** | 3-7 días | < 1h | < 5s |

### **Patrones de Retry y Recuperación**

```yaml
retry_patterns:
  critical_events:
    max_retries: 5
    backoff: "exponential"  # 1s, 2s, 4s, 8s, 16s
    dlq_after: 5_failures
    
  business_events:
    max_retries: 3
    backoff: "linear"  # 2s, 2s, 2s
    dlq_after: 3_failures
    
  notification_events:
    max_retries: 10
    backoff: "fixed"  # 1s entre cada retry
    dlq_after: 10_failures
```

### **Monitoreo de Flujos**

```yaml
flow_monitoring:
  correlation_tracking:
    enabled: true
    retention_days: 30
    
  success_rate_alerts:
    onboarding_flow: "> 85%"
    recruitment_flow: "> 70%"
    campaign_flow: "> 95%"
    renewal_flow: "> 90%"
    
  latency_alerts:
    critical_events: "> 10s"
    business_events: "> 30s"
    notification_events: "> 5s"
```

---

Estos flujos proporcionan una guía completa para implementar, monitorear y mantener los procesos de negocio críticos en HexaBuilders, asegurando que todas las interacciones entre servicios sean robustas, observables y escalables.