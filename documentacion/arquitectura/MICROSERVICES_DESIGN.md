# Diseño Detallado de Microservicios - HexaBuilders

## 🎯 Principios de Diseño

### **Bounded Context per Service**
Cada microservicio representa un bounded context específico del dominio, con:
- Modelo de dominio independiente
- Base de datos dedicada
- Ciclo de vida de desarrollo autónomo
- Equipo especializado asignado

### **Event-First Design**
Los servicios se comunican primariamente a través de eventos:
- **Domain Events**: Cambios significativos dentro del contexto
- **Integration Events**: Comunicación entre contextos
- **Command Events**: Solicitudes de acción entre servicios

---

## 🏢 1. Partner Management Service

### **Contexto de Negocio**
Gestión integral del ciclo de vida de partners empresariales, desde el registro inicial hasta las métricas de rendimiento avanzadas.

### **Arquitectura Interna**
```
src/partner_management/
├── seedwork/                 # 🏗️ Infraestructura compartida
│   ├── dominio/             # Entidades base, eventos, excepciones
│   ├── aplicacion/          # Comandos, queries, handlers
│   ├── infraestructura/     # UoW, utils, schema registry
│   └── presentacion/        # API factory, middleware
├── modulos/
│   ├── partners/            # 👥 Gestión de partners
│   │   ├── dominio/         # Partner entity, value objects
│   │   ├── aplicacion/      # Create/Update/Activate commands
│   │   └── infraestructura/ # Repository, DTOs, factories
│   ├── campaigns/           # 📊 Campañas asociadas
│   ├── commissions/         # 💰 Comisiones y pagos
│   └── analytics/           # 📈 Métricas y reportes
└── api/                     # 🌐 CQRS API endpoints
```

### **Entidades Principales**
- **Partner**: Aggregate root con estados complejos
- **Campaign**: Campañas de marketing y rendimiento
- **Commission**: Cálculos y histórico de pagos
- **Report**: Analytics y métricas 360°

### **Eventos de Dominio**
```python
# Eventos internos del servicio
PartnerCreated(partner_id, business_name, email, type)
PartnerStatusChanged(partner_id, old_status, new_status)
PartnerActivated(partner_id, activation_reason)
CampaignAssigned(partner_id, campaign_id)
CommissionCalculated(partner_id, amount, period)
```

### **Integration Events**
```python
# Eventos hacia otros servicios
PartnerRegistrationCompleted → Onboarding
PartnerValidationCompleted → Campaign Management
RecruitmentRequested → Recruitment
PartnerMetricsUpdated → Analytics Service
```

---

## 📋 2. Onboarding Service

### **Contexto de Negocio**
Gestión del proceso legal y contractual para nuevos partners, incluyendo negociación de términos, validación legal y documentación completa.

### **Arquitectura Interna**
```
src/onboarding/
├── seedwork/                 # 🏗️ Infraestructura compartida
├── modulos/
│   ├── contracts/           # 📄 Gestión de contratos
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Contract, ContractTerm
│   │   │   ├── objetos_valor.py   # ContractStatus, LegalTerms
│   │   │   └── eventos.py         # ContractCreated, ContractSigned
│   │   ├── aplicacion/
│   │   │   ├── comandos/          # CreateContract, SignContract
│   │   │   └── queries/           # GetContract, GetContractHistory
│   │   └── infraestructura/       # Repository, DTOs
│   ├── negotiations/        # 🤝 Proceso de negociación
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Negotiation, NegotiationRound
│   │   │   ├── objetos_valor.py   # NegotiationStatus, Proposal
│   │   │   └── eventos.py         # NegotiationStarted, ProposalSubmitted
│   │   └── aplicacion/            # Negotiation commands/queries
│   ├── legal/               # ⚖️ Validación legal
│   │   ├── dominio/
│   │   │   ├── entidades.py       # LegalValidation, ComplianceCheck
│   │   │   └── eventos.py         # LegalValidationCompleted
│   │   └── aplicacion/            # Validation commands
│   └── documents/           # 📋 Gestión documental
│       ├── dominio/
│       │   ├── entidades.py       # Document, DigitalSignature
│       │   └── eventos.py         # DocumentUploaded, DocumentSigned
│       └── aplicacion/            # Document management
└── api/                     # 🌐 Contract CQRS API
```

### **Entidades Principales**
- **Contract**: Aggregate root del proceso contractual
- **Negotiation**: Proceso de negociación de términos
- **LegalValidation**: Validaciones legales y compliance
- **Document**: Documentos y firmas digitales

### **Estados del Contrato**
```python
class ContractStatus(Enum):
    DRAFT = "DRAFT"                    # Borrador inicial
    IN_NEGOTIATION = "IN_NEGOTIATION"  # En proceso de negociación
    LEGAL_REVIEW = "LEGAL_REVIEW"      # Revisión legal
    PENDING_SIGNATURE = "PENDING_SIGNATURE"  # Esperando firmas
    SIGNED = "SIGNED"                  # Firmado completamente
    ACTIVE = "ACTIVE"                  # Contrato activo
    EXPIRED = "EXPIRED"                # Contrato vencido
    TERMINATED = "TERMINATED"          # Terminado anticipadamente
```

### **Eventos de Dominio**
```python
# Contratos
ContractCreated(contract_id, partner_id, terms)
ContractTermsNegotiated(contract_id, old_terms, new_terms)
ContractSigned(contract_id, signatories, timestamp)
ContractActivated(contract_id, activation_date)

# Negociaciones
NegotiationStarted(negotiation_id, contract_id, participants)
ProposalSubmitted(negotiation_id, proposal_details, submitted_by)
NegotiationConcluded(negotiation_id, final_terms, agreement_status)

# Legal
LegalValidationRequested(contract_id, validation_type)
LegalValidationCompleted(contract_id, validation_result, compliance_status)

# Documentos
DocumentUploaded(document_id, contract_id, document_type)
DigitalSignatureApplied(document_id, signatory, signature_data)
```

### **Integration Events**
```python
# Desde Partner Management
PartnerRegistrationCompleted → Inicia proceso de contrato

# Hacia otros servicios
ContractSigned → Partner Management (Actualizar estado)
ContractActivated → Campaign Management (Habilitar campañas)
LegalValidationCompleted → Partner Management (Actualizar validación)
```

---

## 👥 3. Recruitment Service

### **Contexto de Negocio**
Marketplace de talentos que conecta partners con candidatos calificados, incluyendo matching inteligente y gestión del proceso de entrevistas.

### **Arquitectura Interna**
```
src/recruitment/
├── seedwork/                 # 🏗️ Infraestructura compartida
├── modulos/
│   ├── candidates/          # 👤 Gestión de candidatos
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Candidate, CandidateProfile
│   │   │   ├── objetos_valor.py   # Skills, Experience, Education
│   │   │   └── eventos.py         # CandidateRegistered, ProfileUpdated
│   │   ├── aplicacion/
│   │   │   ├── comandos/          # RegisterCandidate, UpdateProfile
│   │   │   └── queries/           # SearchCandidates, GetProfile
│   │   └── infraestructura/       # Repository, Search engine
│   ├── jobs/                # 💼 Ofertas laborales
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Job, JobRequirements
│   │   │   ├── objetos_valor.py   # JobType, Salary, Location
│   │   │   └── eventos.py         # JobPosted, JobFilled
│   │   └── aplicacion/            # Job management commands
│   ├── matching/            # 🎯 Algoritmos de matching
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Match, MatchingCriteria
│   │   │   ├── objetos_valor.py   # MatchScore, MatchReason
│   │   │   └── eventos.py         # MatchFound, MatchRanked
│   │   └── aplicacion/
│   │       ├── algoritmos/        # Matching algorithms
│   │       └── servicios/         # Matching services
│   └── interviews/          # 📞 Gestión de entrevistas
│       ├── dominio/
│       │   ├── entidades.py       # Interview, InterviewFeedback
│       │   ├── objetos_valor.py   # InterviewType, Rating
│       │   └── eventos.py         # InterviewScheduled, InterviewCompleted
│       └── aplicacion/            # Interview management
└── api/                     # 🌐 Recruitment API
```

### **Entidades Principales**
- **Candidate**: Perfiles de candidatos con skills y experiencia
- **Job**: Ofertas laborales con requisitos específicos
- **Match**: Resultado de matching candidato-trabajo
- **Interview**: Proceso de entrevistas y evaluaciones

### **Algoritmos de Matching**
```python
class MatchingCriteria:
    skill_weight: float = 0.4      # 40% skills técnicos
    experience_weight: float = 0.3  # 30% experiencia
    education_weight: float = 0.2   # 20% educación
    location_weight: float = 0.1    # 10% ubicación

class MatchScore:
    total_score: float           # 0.0 - 1.0
    skill_match: float
    experience_match: float
    education_match: float
    location_match: float
    match_reasons: List[str]
```

### **Eventos de Dominio**
```python
# Candidatos
CandidateRegistered(candidate_id, basic_info, source)
CandidateProfileUpdated(candidate_id, updated_fields)
CandidateSkillsUpdated(candidate_id, new_skills, skill_level)

# Trabajos
JobPosted(job_id, partner_id, requirements, salary_range)
JobRequirementsUpdated(job_id, new_requirements)
JobFilled(job_id, selected_candidate_id)

# Matching
MatchingRequested(job_id, criteria, max_candidates)
MatchFound(match_id, job_id, candidate_id, match_score)
MatchRankingCompleted(job_id, ranked_matches)

# Entrevistas
InterviewScheduled(interview_id, job_id, candidate_id, datetime)
InterviewFeedbackSubmitted(interview_id, feedback, rating)
CandidateHired(candidate_id, job_id, partner_id, start_date)
```

### **Integration Events**
```python
# Desde Partner Management
RecruitmentRequested → Inicia búsqueda de candidatos

# Hacia otros servicios
CandidateMatched → Partner Management (Notificar matches)
CandidateHired → Partner Management (Actualizar métricas)
CandidateHired → Onboarding (Proceso contractual empleado)
```

---

## 📊 4. Campaign Management Service

### **Contexto de Negocio**
Gestión avanzada del ciclo de vida completo de campañas de marketing, incluyendo segmentación inteligente, métricas en tiempo real y control presupuestario.

### **Arquitectura Interna**
```
src/campaign_management/
├── seedwork/                 # 🏗️ Infraestructura compartida
├── modulos/
│   ├── campaigns/           # 🎯 Gestión de campañas
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Campaign, CampaignGoal
│   │   │   ├── objetos_valor.py   # CampaignType, Status, Duration
│   │   │   └── eventos.py         # CampaignCreated, CampaignLaunched
│   │   ├── aplicacion/
│   │   │   ├── comandos/          # CreateCampaign, LaunchCampaign
│   │   │   └── queries/           # GetCampaign, GetCampaignMetrics
│   │   └── infraestructura/       # Repository, metrics storage
│   ├── targeting/           # 🎯 Segmentación de audiencias
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Audience, Segment
│   │   │   ├── objetos_valor.py   # Demographics, Interests
│   │   │   └── eventos.py         # AudienceCreated, SegmentDefined
│   │   └── aplicacion/
│   │       ├── algoritmos/        # Segmentation algorithms
│   │       └── servicios/         # Targeting services
│   ├── performance/         # 📈 Métricas en tiempo real
│   │   ├── dominio/
│   │   │   ├── entidades.py       # Metric, KPI, PerformanceReport
│   │   │   ├── objetos_valor.py   # MetricType, MetricValue
│   │   │   └── eventos.py         # MetricUpdated, ThresholdReached
│   │   ├── aplicacion/
│   │   │   └── real_time/         # Real-time metrics processing
│   │   └── infraestructura/       # Time series database
│   └── budgets/             # 💰 Control presupuestario
│       ├── dominio/
│       │   ├── entidades.py       # Budget, BudgetAllocation
│       │   ├── objetos_valor.py   # BudgetType, Allocation
│       │   └── eventos.py         # BudgetCreated, BudgetExceeded
│       └── aplicacion/            # Budget management
└── api/                     # 🌐 Campaign CQRS API
```

### **Entidades Principales**
- **Campaign**: Aggregate root con ciclo de vida complejo
- **Audience**: Segmentación y targeting de audiencias
- **Metric**: KPIs y métricas de rendimiento en tiempo real
- **Budget**: Control presupuestario y allocaciones

### **Estados de Campaña**
```python
class CampaignStatus(Enum):
    DRAFT = "DRAFT"                # Borrador en creación
    PLANNING = "PLANNING"          # En planificación
    APPROVED = "APPROVED"          # Aprobada para lanzamiento
    SCHEDULED = "SCHEDULED"        # Programada para inicio
    ACTIVE = "ACTIVE"              # Activa y ejecutándose
    PAUSED = "PAUSED"              # Pausada temporalmente
    COMPLETED = "COMPLETED"        # Completada exitosamente
    CANCELLED = "CANCELLED"        # Cancelada antes de completar
    FAILED = "FAILED"              # Falló durante ejecución
```

### **Métricas en Tiempo Real**
```python
class CampaignMetrics:
    # Métricas de alcance
    impressions: int
    reach: int
    frequency: float
    
    # Métricas de engagement
    clicks: int
    ctr: float  # Click-through rate
    engagement_rate: float
    
    # Métricas de conversión
    conversions: int
    conversion_rate: float
    cost_per_conversion: float
    
    # Métricas financieras
    spend: float
    budget_utilization: float
    roi: float  # Return on investment
```

### **Eventos de Dominio**
```python
# Campañas
CampaignCreated(campaign_id, partner_id, campaign_type, goals)
CampaignLaunched(campaign_id, launch_date, initial_budget)
CampaignCompleted(campaign_id, final_metrics, success_status)

# Targeting
AudienceSegmentCreated(segment_id, criteria, estimated_size)
TargetingOptimized(campaign_id, old_targeting, new_targeting)

# Performance (Event Sourcing)
MetricUpdated(campaign_id, metric_type, old_value, new_value, timestamp)
KPIThresholdReached(campaign_id, kpi_type, threshold_value, actual_value)
PerformanceAnomalyDetected(campaign_id, anomaly_type, severity)

# Presupuesto
BudgetAllocated(campaign_id, budget_amount, allocation_breakdown)
BudgetThresholdReached(campaign_id, threshold_percentage, current_spend)
BudgetExceeded(campaign_id, budget_limit, actual_spend, exceeded_by)
```

### **Integration Events**
```python
# Desde otros servicios
ContractActivated → Habilita creación de campañas
PartnerValidationCompleted → Actualiza permisos de campaña

# Hacia otros servicios
CampaignLaunched → Partner Management (Actualizar métricas)
BudgetExceeded → Partner Management + Notifications
CampaignCompleted → Partner Management + Analytics
PerformanceReport → Analytics Service
```

---

## 🔄 Patrones de Comunicación

### **Command Pattern**
```python
# Ejemplo: Creación de campaña tras activación de contrato
@event_handler
def on_contract_activated(event: ContractActivated):
    command = EnableCampaignCreation(
        partner_id=event.partner_id,
        contract_id=event.contract_id,
        permissions=event.campaign_permissions
    )
    command_bus.dispatch(command)
```

### **Query Pattern**
```python
# Ejemplo: Consulta síncrona de perfil para matching
async def get_partner_profile_for_matching(partner_id: str) -> PartnerProfile:
    response = await http_client.get(
        f"http://partner-management:5000/api/v1/partners-query/{partner_id}/profile-360"
    )
    return PartnerProfile.from_dict(response.json())
```

### **Event Sourcing Pattern**
```python
# Ejemplo: Reconstrucción de métricas de campaña
def rebuild_campaign_metrics(campaign_id: str) -> CampaignMetrics:
    events = event_store.get_events(campaign_id)
    metrics = CampaignMetrics()
    
    for event in events:
        if isinstance(event, MetricUpdated):
            metrics.apply_metric_update(event)
        elif isinstance(event, BudgetAllocated):
            metrics.apply_budget_change(event)
    
    return metrics
```

---

Esta arquitectura de microservicios proporciona una base sólida, escalable y mantenible para el crecimiento futuro de HexaBuilders, manteniendo la coherencia del dominio mientras permite la evolución independiente de cada contexto de negocio.