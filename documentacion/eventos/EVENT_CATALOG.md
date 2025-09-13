# Catálogo Completo de Eventos - HexaBuilders

## 📋 Índice de Eventos

| Servicio | Domain Events | Integration Events | Total |
|----------|---------------|-------------------|-------|
| **Partner Management** | 11 | 4 | 15 |
| **Onboarding** | 12 | 3 | 15 |
| **Recruitment** | 10 | 3 | 13 |
| **Campaign Management** | 13 | 4 | 17 |
| **TOTAL** | **46** | **14** | **60** |

---

## 🏢 Partner Management Service Events

### **Domain Events** (Internos al servicio)

#### **Partner Lifecycle Events**
```python
class PartnerCreated(DomainEvent):
    """Se crea un nuevo partner en el sistema"""
    aggregate_id: str      # partner_id
    business_name: str     # Nombre del negocio
    email: str             # Email principal
    partner_type: str      # INDIVIDUAL, EMPRESA, STARTUP
    phone: str             # Teléfono de contacto
    registration_source: str  # WEB, API, REFERRAL
```

```python
class PartnerStatusChanged(DomainEvent):
    """Cambio de estado del partner"""
    aggregate_id: str      # partner_id
    old_status: str        # Estado anterior
    new_status: str        # Nuevo estado
    reason: str            # Razón del cambio
    changed_by: str        # Usuario que realizó el cambio
```

```python
class PartnerActivated(DomainEvent):
    """Partner activado para operaciones"""
    aggregate_id: str      # partner_id
    partner_email: str     # Email del partner
    partner_name: str      # Nombre del partner
    activation_date: str   # Fecha de activación
    activated_by: str      # Usuario que activó
```

```python
class PartnerDeactivated(DomainEvent):
    """Partner desactivado"""
    aggregate_id: str      # partner_id
    partner_email: str     # Email del partner
    partner_name: str      # Nombre del partner
    deactivation_reason: str  # Razón de desactivación
    deactivated_by: str    # Usuario que desactivó
```

```python
class PartnerUpdated(DomainEvent):
    """Información del partner actualizada"""
    aggregate_id: str      # partner_id
    old_data: dict         # Datos anteriores
    new_data: dict         # Datos nuevos
    updated_fields: list   # Campos específicos actualizados
    updated_by: str        # Usuario que actualizó
```

```python
class PartnerValidationCompleted(DomainEvent):
    """Validación del partner completada"""
    aggregate_id: str      # partner_id
    validation_type: str   # EMAIL, PHONE, IDENTITY, BUSINESS
    partner_email: str     # Email del partner
    validation_result: bool # Resultado de la validación
    validation_data: dict  # Datos adicionales de validación
```

#### **Campaign Events**
```python
class CampaignAssigned(DomainEvent):
    """Campaña asignada a partner"""
    aggregate_id: str      # partner_id
    campaign_id: str       # ID de la campaña
    assignment_type: str   # AUTOMATIC, MANUAL
    assigned_by: str       # Usuario que asignó
    assignment_criteria: dict  # Criterios de asignación
```

```python
class CampaignPerformanceUpdated(DomainEvent):
    """Rendimiento de campaña actualizado"""
    aggregate_id: str      # partner_id
    campaign_id: str       # ID de la campaña
    performance_metrics: dict  # Métricas de rendimiento
    update_source: str     # REALTIME, BATCH, MANUAL
```

#### **Commission Events**
```python
class CommissionCalculated(DomainEvent):
    """Comisión calculada para partner"""
    aggregate_id: str      # partner_id
    commission_id: str     # ID de la comisión
    amount: float          # Monto de la comisión
    currency: str          # Moneda
    calculation_period: dict  # Período de cálculo
    calculation_method: str   # Método utilizado
```

```python
class CommissionPaid(DomainEvent):
    """Comisión pagada al partner"""
    aggregate_id: str      # partner_id
    commission_id: str     # ID de la comisión
    payment_amount: float  # Monto pagado
    payment_method: str    # Método de pago
    payment_reference: str # Referencia del pago
    payment_date: str      # Fecha de pago
```

#### **Analytics Events**
```python
class PartnerMetricsUpdated(DomainEvent):
    """Métricas del partner actualizadas"""
    aggregate_id: str      # partner_id
    old_metrics: dict      # Métricas anteriores
    new_metrics: dict      # Métricas nuevas
    metric_source: str     # CAMPAIGN, COMMISSION, MANUAL
    calculation_timestamp: str  # Momento del cálculo
```

### **Integration Events** (Entre servicios)

```python
class PartnerRegistrationCompleted(IntegrationEvent):
    """Partner completó registro → Onboarding"""
    aggregate_id: str      # partner_id
    business_name: str     # Nombre del negocio
    email: str             # Email del partner
    partner_type: str      # Tipo de partner
    registration_data: dict    # Datos completos de registro
    
    # Topic: partner-management/partner-registration
    # Consumers: onboarding-service
```

```python
class PartnerValidationCompleted(IntegrationEvent):
    """Validación completada → Campaign Management"""
    aggregate_id: str      # partner_id
    partner_email: str     # Email del partner
    validation_status: str # FULLY_VALIDATED, PARTIALLY_VALIDATED
    validation_details: dict   # Detalles de validación
    
    # Topic: partner-management/partner-validation
    # Consumers: campaign-management-service
```

```python
class RecruitmentRequested(IntegrationEvent):
    """Solicitud de reclutamiento → Recruitment"""
    aggregate_id: str      # partner_id
    job_requirements: dict # Requisitos del trabajo
    urgency_level: str     # LOW, NORMAL, HIGH, URGENT
    budget_range: dict     # Rango presupuestario
    
    # Topic: partner-management/recruitment-requests
    # Consumers: recruitment-service
```

```python
class PartnerMetricsSnapshot(IntegrationEvent):
    """Snapshot de métricas → Analytics Services"""
    aggregate_id: str      # partner_id
    metrics_snapshot: dict # Snapshot completo de métricas
    snapshot_timestamp: str    # Momento del snapshot
    snapshot_reason: str   # PERIODIC, ON_DEMAND, TRIGGER
    
    # Topic: partner-management/metrics-snapshots
    # Consumers: analytics-service, reporting-service
```

---

## 📋 Onboarding Service Events

### **Domain Events**

#### **Contract Events**
```python
class ContractCreated(DomainEvent):
    """Nuevo contrato creado"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner
    contract_type: str     # STANDARD, CUSTOM, ENTERPRISE
    initial_terms: dict    # Términos iniciales
    created_by: str        # Usuario que creó
```

```python
class ContractTermsNegotiated(DomainEvent):
    """Términos del contrato negociados"""
    aggregate_id: str      # contract_id
    negotiation_round: int # Ronda de negociación
    old_terms: dict        # Términos anteriores
    new_terms: dict        # Términos propuestos
    negotiated_by: str     # Quien negoció
```

```python
class ContractSigned(DomainEvent):
    """Contrato firmado por todas las partes"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner
    signatories: list      # Lista de firmantes
    signature_data: dict   # Datos de firmas digitales
    final_terms: dict      # Términos finales
    signature_timestamp: str   # Momento de la firma
```

```python
class ContractActivated(DomainEvent):
    """Contrato activado y en vigor"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner
    activation_date: str   # Fecha de activación
    contract_duration: dict    # Duración del contrato
    renewal_terms: dict    # Términos de renovación
```

#### **Negotiation Events**
```python
class NegotiationStarted(DomainEvent):
    """Proceso de negociación iniciado"""
    aggregate_id: str      # negotiation_id
    contract_id: str       # ID del contrato
    participants: list     # Participantes en la negociación
    initial_proposal: dict # Propuesta inicial
    negotiation_deadline: str  # Fecha límite
```

```python
class ProposalSubmitted(DomainEvent):
    """Nueva propuesta enviada"""
    aggregate_id: str      # negotiation_id
    proposal_id: str       # ID de la propuesta
    submitted_by: str      # Quien envió la propuesta
    proposal_details: dict # Detalles de la propuesta
    submission_timestamp: str  # Momento del envío
```

```python
class NegotiationConcluded(DomainEvent):
    """Negociación finalizada"""
    aggregate_id: str      # negotiation_id
    contract_id: str       # ID del contrato
    final_terms: dict      # Términos finales acordados
    conclusion_reason: str # AGREEMENT, TIMEOUT, CANCELLED
    concluded_by: str      # Quien concluyó
```

#### **Legal Events**
```python
class LegalValidationRequested(DomainEvent):
    """Solicitud de validación legal"""
    aggregate_id: str      # validation_id
    contract_id: str       # ID del contrato
    validation_type: str   # COMPLIANCE, REGULATORY, CUSTOM
    validation_criteria: dict  # Criterios de validación
    requested_by: str      # Quien solicitó
```

```python
class LegalValidationCompleted(DomainEvent):
    """Validación legal completada"""
    aggregate_id: str      # validation_id
    contract_id: str       # ID del contrato
    validation_result: str # APPROVED, REJECTED, CONDITIONAL
    validation_notes: str  # Notas del validador
    compliance_status: dict    # Estado de cumplimiento
```

#### **Document Events**
```python
class DocumentUploaded(DomainEvent):
    """Documento subido al sistema"""
    aggregate_id: str      # document_id
    contract_id: str       # ID del contrato
    document_type: str     # CONTRACT, ADDENDUM, EVIDENCE
    document_metadata: dict    # Metadatos del documento
    uploaded_by: str       # Usuario que subió
```

```python
class DocumentVersionCreated(DomainEvent):
    """Nueva versión de documento creada"""
    aggregate_id: str      # document_id
    version_number: str    # Número de versión
    version_changes: dict  # Cambios en esta versión
    created_by: str        # Quien creó la versión
```

```python
class DigitalSignatureApplied(DomainEvent):
    """Firma digital aplicada al documento"""
    aggregate_id: str      # document_id
    signatory_id: str      # ID del firmante
    signature_data: dict   # Datos de la firma digital
    signature_timestamp: str   # Momento de la firma
    signature_valid: bool  # Validez de la firma
```

### **Integration Events**

```python
class ContractSigningCompleted(IntegrationEvent):
    """Contrato firmado → Partner Management"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner
    contract_terms: dict   # Términos del contrato
    effective_date: str    # Fecha efectiva
    
    # Topic: onboarding/contract-signed
    # Consumers: partner-management-service
```

```python
class ContractActivated(IntegrationEvent):
    """Contrato activado → Campaign Management"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner
    campaign_permissions: list # Permisos de campaña
    budget_limits: dict    # Límites presupuestarios
    
    # Topic: onboarding/contract-activated
    # Consumers: campaign-management-service
```

```python
class EmploymentContractSigned(IntegrationEvent):
    """Contrato laboral firmado → Recruitment"""
    aggregate_id: str      # contract_id
    partner_id: str        # ID del partner empleador
    candidate_id: str      # ID del candidato
    employment_terms: dict # Términos laborales
    start_date: str        # Fecha de inicio
    
    # Topic: onboarding/employment-contract
    # Consumers: recruitment-service
```

---

## 👥 Recruitment Service Events

### **Domain Events**

#### **Candidate Events**
```python
class CandidateRegistered(DomainEvent):
    """Nuevo candidato registrado"""
    aggregate_id: str      # candidate_id
    basic_info: dict       # Información básica
    registration_source: str   # WEBSITE, REFERRAL, HEADHUNTER
    initial_skills: list   # Skills iniciales
    availability_status: str   # AVAILABLE, EMPLOYED, NOT_AVAILABLE
```

```python
class CandidateProfileUpdated(DomainEvent):
    """Perfil de candidato actualizado"""
    aggregate_id: str      # candidate_id
    updated_sections: list # Secciones actualizadas
    old_profile_data: dict # Datos del perfil anterior
    new_profile_data: dict # Datos del nuevo perfil
    update_source: str     # SELF, RECRUITER, SYSTEM
```

```python
class CandidateSkillsUpdated(DomainEvent):
    """Skills del candidato actualizados"""
    aggregate_id: str      # candidate_id
    added_skills: list     # Skills añadidas
    removed_skills: list   # Skills eliminadas
    updated_skill_levels: dict # Niveles actualizados
    verification_status: dict  # Estado de verificación
```

#### **Job Events**
```python
class JobPosted(DomainEvent):
    """Nueva oferta laboral publicada"""
    aggregate_id: str      # job_id
    partner_id: str        # ID del partner empleador
    job_title: str         # Título del trabajo
    requirements: dict     # Requisitos del trabajo
    salary_range: dict     # Rango salarial
    job_type: str          # FULL_TIME, PART_TIME, CONTRACT
```

```python
class JobRequirementsUpdated(DomainEvent):
    """Requisitos del trabajo actualizados"""
    aggregate_id: str      # job_id
    old_requirements: dict # Requisitos anteriores
    new_requirements: dict # Nuevos requisitos
    updated_by: str        # Usuario que actualizó
    update_reason: str     # Razón de la actualización
```

```python
class JobStatusChanged(DomainEvent):
    """Estado del trabajo cambió"""
    aggregate_id: str      # job_id
    old_status: str        # Estado anterior
    new_status: str        # Nuevo estado
    status_reason: str     # Razón del cambio
    changed_by: str        # Quien cambió el estado
```

#### **Matching Events**
```python
class MatchingRequested(DomainEvent):
    """Solicitud de matching iniciada"""
    aggregate_id: str      # matching_request_id
    job_id: str            # ID del trabajo
    matching_criteria: dict    # Criterios de matching
    max_candidates: int    # Máximo número de candidatos
    priority_level: str    # LOW, NORMAL, HIGH, URGENT
```

```python
class MatchFound(DomainEvent):
    """Match encontrado entre candidato y trabajo"""
    aggregate_id: str      # match_id
    job_id: str            # ID del trabajo
    candidate_id: str      # ID del candidato
    match_score: float     # Puntuación de matching (0.0-1.0)
    match_reasons: list    # Razones del match
    match_confidence: str  # LOW, MEDIUM, HIGH
```

```python
class MatchRankingCompleted(DomainEvent):
    """Ranking de matches completado"""
    aggregate_id: str      # job_id
    ranked_matches: list   # Lista ordenada de matches
    ranking_algorithm: str # Algoritmo utilizado
    ranking_timestamp: str # Momento del ranking
```

#### **Interview Events**
```python
class InterviewScheduled(DomainEvent):
    """Entrevista programada"""
    aggregate_id: str      # interview_id
    job_id: str            # ID del trabajo
    candidate_id: str      # ID del candidato
    interview_datetime: str    # Fecha y hora
    interview_type: str    # PHONE, VIDEO, IN_PERSON
    interviewer_id: str    # ID del entrevistador
```

```python
class InterviewCompleted(DomainEvent):
    """Entrevista completada"""
    aggregate_id: str      # interview_id
    completion_status: str # COMPLETED, CANCELLED, NO_SHOW
    interview_duration: int    # Duración en minutos
    completion_notes: str  # Notas de la entrevista
```

```python
class InterviewFeedbackSubmitted(DomainEvent):
    """Feedback de entrevista enviado"""
    aggregate_id: str      # interview_id
    feedback_data: dict    # Datos del feedback
    overall_rating: float  # Calificación general (1.0-5.0)
    recommendation: str    # HIRE, NO_HIRE, MAYBE
    submitted_by: str      # Quien envió el feedback
```

### **Integration Events**

```python
class CandidateMatched(IntegrationEvent):
    """Candidato encontrado → Partner Management"""
    aggregate_id: str      # match_id
    partner_id: str        # ID del partner
    candidate_summary: dict    # Resumen del candidato
    match_score: float     # Puntuación del match
    
    # Topic: recruitment/candidate-matched
    # Consumers: partner-management-service
```

```python
class CandidateHired(IntegrationEvent):
    """Candidato contratado → Multiple Services"""
    aggregate_id: str      # hiring_id
    partner_id: str        # ID del partner empleador
    candidate_id: str      # ID del candidato
    job_id: str            # ID del trabajo
    employment_details: dict   # Detalles del empleo
    start_date: str        # Fecha de inicio
    
    # Topic: recruitment/candidate-hired
    # Consumers: partner-management, onboarding-service
```

```python
class RecruitmentCompleted(IntegrationEvent):
    """Proceso de reclutamiento completado"""
    aggregate_id: str      # recruitment_process_id
    partner_id: str        # ID del partner
    job_id: str            # ID del trabajo
    hired_candidate_id: str    # ID del candidato contratado
    process_metrics: dict  # Métricas del proceso
    
    # Topic: recruitment/recruitment-completed
    # Consumers: partner-management-service
```

---

## 📊 Campaign Management Service Events

### **Domain Events**

#### **Campaign Lifecycle Events**
```python
class CampaignCreated(DomainEvent):
    """Nueva campaña creada"""
    aggregate_id: str      # campaign_id
    partner_id: str        # ID del partner
    campaign_name: str     # Nombre de la campaña
    campaign_type: str     # AWARENESS, CONVERSION, RETENTION
    campaign_goals: dict   # Objetivos de la campaña
    initial_budget: float  # Presupuesto inicial
```

```python
class CampaignLaunched(DomainEvent):
    """Campaña lanzada y activa"""
    aggregate_id: str      # campaign_id
    launch_timestamp: str  # Momento del lanzamiento
    initial_targeting: dict    # Targeting inicial
    launch_checklist: dict # Checklist de lanzamiento
    launched_by: str       # Usuario que lanzó
```

```python
class CampaignStatusChanged(DomainEvent):
    """Estado de la campaña cambió"""
    aggregate_id: str      # campaign_id
    old_status: str        # Estado anterior
    new_status: str        # Nuevo estado
    status_reason: str     # Razón del cambio
    changed_by: str        # Usuario que cambió
```

```python
class CampaignCompleted(DomainEvent):
    """Campaña completada"""
    aggregate_id: str      # campaign_id
    completion_reason: str # SCHEDULED, BUDGET_EXHAUSTED, MANUAL
    final_metrics: dict    # Métricas finales
    completion_timestamp: str  # Momento de completación
    success_indicators: dict   # Indicadores de éxito
```

#### **Targeting Events**
```python
class AudienceSegmentCreated(DomainEvent):
    """Nuevo segmento de audiencia creado"""
    aggregate_id: str      # segment_id
    campaign_id: str       # ID de la campaña
    segment_criteria: dict # Criterios de segmentación
    estimated_size: int    # Tamaño estimado
    creation_method: str   # MANUAL, AI_ASSISTED, TEMPLATE
```

```python
class TargetingOptimized(DomainEvent):
    """Targeting optimizado automáticamente"""
    aggregate_id: str      # campaign_id
    optimization_type: str # DEMOGRAPHIC, BEHAVIORAL, PERFORMANCE
    old_targeting: dict    # Targeting anterior
    new_targeting: dict    # Nuevo targeting
    optimization_reason: str   # Razón de la optimización
    expected_improvement: dict # Mejora esperada
```

#### **Performance Events** (Event Sourcing)
```python
class MetricUpdated(DomainEvent):
    """Métrica de campaña actualizada"""
    aggregate_id: str      # campaign_id
    metric_type: str       # IMPRESSIONS, CLICKS, CONVERSIONS
    metric_value: float    # Valor de la métrica
    previous_value: float  # Valor anterior
    update_timestamp: str  # Momento de la actualización
    data_source: str       # SOURCE_PLATFORM, MANUAL, ESTIMATED
```

```python
class KPIThresholdReached(DomainEvent):
    """Umbral de KPI alcanzado"""
    aggregate_id: str      # campaign_id
    kpi_type: str          # CTR, CPC, CONVERSION_RATE, ROI
    threshold_type: str    # TARGET_REACHED, WARNING, CRITICAL
    threshold_value: float # Valor del umbral
    actual_value: float    # Valor actual
    alert_level: str       # LOW, MEDIUM, HIGH, CRITICAL
```

```python
class PerformanceAnomalyDetected(DomainEvent):
    """Anomalía de rendimiento detectada"""
    aggregate_id: str      # campaign_id
    anomaly_type: str      # SPIKE, DROP, TREND_CHANGE
    affected_metrics: list # Métricas afectadas
    anomaly_severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    detection_confidence: float    # Confianza en la detección
    suggested_actions: list    # Acciones sugeridas
```

#### **Budget Events**
```python
class BudgetAllocated(DomainEvent):
    """Presupuesto asignado a la campaña"""
    aggregate_id: str      # campaign_id
    total_budget: float    # Presupuesto total
    allocation_breakdown: dict # Desglose de asignación
    budget_period: dict    # Período presupuestario
    allocated_by: str      # Usuario que asignó
```

```python
class BudgetThresholdReached(DomainEvent):
    """Umbral presupuestario alcanzado"""
    aggregate_id: str      # campaign_id
    threshold_percentage: float    # Porcentaje del umbral
    current_spend: float   # Gasto actual
    budget_limit: float    # Límite presupuestario
    days_remaining: int    # Días restantes
    threshold_type: str    # WARNING, CRITICAL, EXHAUSTED
```

```python
class BudgetExceeded(DomainEvent):
    """Presupuesto excedido"""
    aggregate_id: str      # campaign_id
    budget_limit: float    # Límite presupuestario
    actual_spend: float    # Gasto real
    exceeded_by: float     # Cantidad excedida
    exceeded_timestamp: str    # Momento de exceso
    automatic_actions: list    # Acciones automáticas tomadas
```

```python
class BudgetReallocation(DomainEvent):
    """Presupuesto reasignado"""
    aggregate_id: str      # campaign_id
    old_allocation: dict   # Asignación anterior
    new_allocation: dict   # Nueva asignación
    reallocation_reason: str   # Razón de la reasignación
    expected_impact: dict  # Impacto esperado
```

### **Integration Events**

```python
class CampaignPerformanceReport(IntegrationEvent):
    """Reporte de rendimiento → Partner Management + Analytics"""
    aggregate_id: str      # campaign_id
    partner_id: str        # ID del partner
    performance_summary: dict # Resumen de rendimiento
    reporting_period: dict # Período del reporte
    kpi_achievements: dict # Logros de KPIs
    
    # Topic: campaign-management/performance-report
    # Consumers: partner-management, analytics-service
```

```python
class BudgetAlert(IntegrationEvent):
    """Alerta presupuestaria → Partner Management + Notifications"""
    aggregate_id: str      # campaign_id
    partner_id: str        # ID del partner
    alert_type: str        # WARNING, CRITICAL, EXHAUSTED
    budget_status: dict    # Estado presupuestario
    recommended_actions: list  # Acciones recomendadas
    
    # Topic: campaign-management/budget-alerts
    # Consumers: partner-management, notifications-service
```

```python
class CampaignInsights(IntegrationEvent):
    """Insights de campaña → Analytics Services"""
    aggregate_id: str      # campaign_id
    partner_id: str        # ID del partner
    insights_data: dict    # Datos de insights
    insight_type: str      # PERFORMANCE, AUDIENCE, OPTIMIZATION
    confidence_level: float    # Nivel de confianza
    
    # Topic: campaign-management/campaign-insights
    # Consumers: analytics-service, partner-management
```

```python
class OptimizationSuggestion(IntegrationEvent):
    """Sugerencia de optimización → Partner Management"""
    aggregate_id: str      # campaign_id
    partner_id: str        # ID del partner
    optimization_type: str # TARGETING, BUDGET, CREATIVE
    current_performance: dict  # Rendimiento actual
    suggested_changes: dict    # Cambios sugeridos
    expected_improvement: dict # Mejora esperada
    
    # Topic: campaign-management/optimization-suggestions
    # Consumers: partner-management-service
```

---

## 🔄 Flujos de Eventos Cross-Service

### **Flujo 1: Onboarding Completo de Partner**
```
1. Partner Management: PartnerCreated
2. Partner Management: PartnerRegistrationCompleted → Onboarding
3. Onboarding: ContractCreated
4. Onboarding: ContractSigned
5. Onboarding: ContractActivated → Campaign Management + Partner Management
6. Campaign Management: CampaignCreationEnabled
7. Partner Management: PartnerStatusChanged (VALIDATED)
```

### **Flujo 2: Proceso de Reclutamiento**
```
1. Partner Management: RecruitmentRequested → Recruitment
2. Recruitment: MatchingRequested
3. Recruitment: MatchFound
4. Recruitment: CandidateMatched → Partner Management
5. Recruitment: InterviewScheduled
6. Recruitment: CandidateHired → Partner Management + Onboarding
7. Onboarding: EmploymentContractSigned
8. Partner Management: PartnerMetricsUpdated
```

### **Flujo 3: Gestión de Campaña Completa**
```
1. Campaign Management: CampaignCreated
2. Campaign Management: CampaignLaunched
3. Campaign Management: MetricUpdated (múltiples)
4. Campaign Management: BudgetThresholdReached
5. Campaign Management: BudgetAlert → Partner Management
6. Campaign Management: CampaignCompleted
7. Campaign Management: CampaignPerformanceReport → Partner Management
8. Partner Management: PartnerMetricsUpdated
```

---

## 📊 Métricas de Eventos

### **Volumen Estimado por Servicio (por día)**
| Servicio | Domain Events | Integration Events | Total Diario |
|----------|---------------|-------------------|--------------|
| Partner Management | ~500 | ~50 | ~550 |
| Onboarding | ~200 | ~30 | ~230 |
| Recruitment | ~300 | ~25 | ~325 |
| Campaign Management | ~2000 | ~100 | ~2100 |
| **TOTAL** | **~3000** | **~205** | **~3205** |

### **Patrones de Retención**
- **Domain Events**: 2 años (auditoría y reconstrucción)
- **Integration Events**: 1 año (troubleshooting)
- **Performance Events**: 5 años (análisis histórico)
- **Contractual Events**: Permanente (requisitos legales)

---

Este catálogo proporciona la base completa para la implementación del sistema de eventos en HexaBuilders, asegurando trazabilidad, auditoría y comunicación eficiente entre todos los microservicios.