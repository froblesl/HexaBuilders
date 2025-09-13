# Onboarding Service Design - HexaBuilders

## 🎯 Contexto de Negocio

El **Onboarding Service** gestiona el proceso legal y contractual completo para partners de HexaBuilders, desde la negociación inicial hasta la activación del contrato. Este servicio crítico maneja:

- 📄 **Gestión contractual** completa con versionado
- 🤝 **Procesos de negociación** estructurados  
- ⚖️ **Validaciones legales** y compliance
- 📋 **Documentación digital** con firmas electrónicas
- 🔒 **Auditoría completa** de todos los procesos

---

## 🏗️ Arquitectura del Servicio

### **Patrón de Almacenamiento**: Event Sourcing
**Justificación**: Los contratos legales requieren trazabilidad absoluta, capacidad de reconstruir el historial completo de negociaciones y auditoría para compliance regulatorio.

```
┌─────────────────────────────────────────────────────────────┐
│                  Onboarding Service                         │
├─────────────────────────────────────────────────────────────┤
│  📋 API Layer (Flask CQRS)                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Contracts   │ │Negotiations │ │ Legal Docs  │          │
│  │ Controller  │ │ Controller  │ │ Controller  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🔄 Application Layer                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Commands   │ │   Queries   │ │  Handlers   │          │
│  │  & Events   │ │  & DTOs     │ │ & Services  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🏛️ Domain Layer                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Aggregates  │ │Value Objects│ │Domain Events│          │
│  │& Entities   │ │& Rules      │ │& Services   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🔌 Infrastructure Layer                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │Event Store  │ │Pulsar Queue │ │External APIs│          │
│  │(PostgreSQL) │ │Integration  │ │(DocuSign)   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Módulos

```
src/onboarding/
├── seedwork/                    # 🏗️ Infraestructura compartida
│   ├── dominio/                # Entidades base, eventos, excepciones
│   ├── aplicacion/             # Comandos, queries, handlers base
│   ├── infraestructura/        # Event store, UoW, adaptadores
│   └── presentacion/           # API factory, middleware
├── modulos/
│   ├── contracts/              # 📄 Gestión de contratos
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Contract (Aggregate Root)
│   │   │   ├── objetos_valor.py       # ContractStatus, Terms, etc.
│   │   │   ├── eventos.py             # Contract domain events
│   │   │   ├── reglas.py              # Business rules
│   │   │   └── repositorio.py         # Contract repository interface
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── crear_contrato.py
│   │   │   │   ├── actualizar_terminos.py
│   │   │   │   ├── firmar_contrato.py
│   │   │   │   └── activar_contrato.py
│   │   │   ├── queries/
│   │   │   │   ├── obtener_contrato.py
│   │   │   │   ├── obtener_historial_contrato.py
│   │   │   │   └── obtener_contratos_por_partner.py
│   │   │   ├── handlers.py             # Command & Query handlers
│   │   │   └── servicios_aplicacion.py # Application services
│   │   └── infraestructura/
│   │       ├── repositorios_evento.py  # Event sourcing repository
│   │       ├── dto.py                  # Data transfer objects
│   │       ├── fabricas.py             # Domain factories
│   │       └── schema/                 # Avro schemas
│   ├── negotiations/           # 🤝 Proceso de negociación
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Negotiation, Round
│   │   │   ├── objetos_valor.py       # Proposal, Terms
│   │   │   ├── eventos.py             # Negotiation events
│   │   │   └── reglas.py              # Negotiation business rules
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── iniciar_negociacion.py
│   │   │   │   ├── enviar_propuesta.py
│   │   │   │   ├── responder_propuesta.py
│   │   │   │   └── finalizar_negociacion.py
│   │   │   └── queries/
│   │   │       ├── obtener_negociacion.py
│   │   │       └── obtener_propuestas.py
│   │   └── infraestructura/
│   │       ├── repositorios_evento.py
│   │       └── servicios_externos.py  # Email, notifications
│   ├── legal/                  # ⚖️ Validación legal
│   │   ├── dominio/
│   │   │   ├── entidades.py           # LegalValidation, ComplianceCheck
│   │   │   ├── objetos_valor.py       # ValidationResult, ComplianceStatus
│   │   │   ├── eventos.py             # Legal validation events
│   │   │   └── reglas.py              # Compliance rules
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── solicitar_validacion.py
│   │   │   │   ├── completar_validacion.py
│   │   │   │   └── aprobar_compliance.py
│   │   │   └── queries/
│   │   │       └── obtener_estado_validacion.py
│   │   └── infraestructura/
│   │       ├── servicios_legales.py   # External legal services
│   │       └── validadores.py         # Automated validators
│   └── documents/              # 📋 Gestión documental
│       ├── dominio/
│       │   ├── entidades.py           # Document, Signature
│       │   ├── objetos_valor.py       # DocumentType, SignatureData
│       │   ├── eventos.py             # Document events
│       │   └── reglas.py              # Document rules
│       ├── aplicacion/
│       │   ├── comandos/
│       │   │   ├── subir_documento.py
│       │   │   ├── firmar_documento.py
│       │   │   └── generar_version.py
│       │   └── queries/
│       │       ├── obtener_documento.py
│       │       └── obtener_versiones.py
│       └── infraestructura/
│           ├── almacenamiento_docs.py # Document storage (S3/MinIO)
│           └── servicios_firma.py     # DocuSign integration
└── api/                        # 🌐 CQRS API endpoints
    ├── contracts_cqrs.py
    ├── negotiations_cqrs.py
    ├── legal_cqrs.py
    └── documents_cqrs.py
```

---

## 🏛️ Diseño del Dominio

### **Aggregate Roots**

#### **1. Contract (Aggregate Root)**
```python
class Contract(AggregateRoot):
    """
    Contrato principal que mantiene la consistencia de todo el proceso contractual.
    """
    def __init__(
        self,
        partner_id: str,
        contract_type: ContractType,
        initial_terms: ContractTerms,
        contract_id: Optional[str] = None
    ):
        super().__init__(contract_id)
        self._partner_id = partner_id
        self._contract_type = contract_type
        self._current_terms = initial_terms
        self._status = ContractStatus.DRAFT
        self._negotiation_history: List[NegotiationRound] = []
        self._signatures: List[DigitalSignature] = []
        self._legal_validations: List[LegalValidation] = []
        
        # Domain event
        self.agregar_evento(ContractCreated(
            aggregate_id=self.id,
            partner_id=partner_id,
            contract_type=contract_type.value,
            initial_terms=initial_terms.to_dict()
        ))
    
    def negotiate_terms(self, new_terms: ContractTerms, negotiated_by: str) -> None:
        """Negociar términos del contrato"""
        if self._status not in [ContractStatus.DRAFT, ContractStatus.IN_NEGOTIATION]:
            raise BusinessRuleException("Cannot negotiate terms in current status")
        
        old_terms = self._current_terms
        self._current_terms = new_terms
        self._status = ContractStatus.IN_NEGOTIATION
        
        negotiation_round = NegotiationRound(
            round_number=len(self._negotiation_history) + 1,
            old_terms=old_terms,
            new_terms=new_terms,
            negotiated_by=negotiated_by,
            timestamp=datetime.utcnow()
        )
        self._negotiation_history.append(negotiation_round)
        
        self.agregar_evento(ContractTermsNegotiated(
            aggregate_id=self.id,
            negotiation_round=negotiation_round.round_number,
            old_terms=old_terms.to_dict(),
            new_terms=new_terms.to_dict(),
            negotiated_by=negotiated_by
        ))
    
    def add_signature(self, signature: DigitalSignature) -> None:
        """Añadir firma digital al contrato"""
        if self._status != ContractStatus.PENDING_SIGNATURE:
            raise BusinessRuleException("Contract not ready for signature")
        
        # Validar que el firmante no haya firmado ya
        if any(s.signatory_id == signature.signatory_id for s in self._signatures):
            raise BusinessRuleException("Signatory has already signed")
        
        self._signatures.append(signature)
        
        # Verificar si todas las firmas requeridas están completas
        required_signatures = self._get_required_signatures()
        if len(self._signatures) >= required_signatures:
            self._status = ContractStatus.SIGNED
            self.agregar_evento(ContractSigned(
                aggregate_id=self.id,
                partner_id=self._partner_id,
                signatories=[s.signatory_id for s in self._signatures],
                signature_data=signature.to_dict(),
                final_terms=self._current_terms.to_dict()
            ))
    
    def activate(self, activation_date: datetime) -> None:
        """Activar contrato firmado"""
        if self._status != ContractStatus.SIGNED:
            raise BusinessRuleException("Contract must be signed before activation")
        
        # Validar que todas las validaciones legales estén completas
        if not self._all_legal_validations_passed():
            raise BusinessRuleException("Legal validations not completed")
        
        self._status = ContractStatus.ACTIVE
        self._activation_date = activation_date
        self._mark_updated()
        
        self.agregar_evento(ContractActivated(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            activation_date=activation_date.isoformat(),
            contract_duration=self._current_terms.duration.to_dict(),
            campaign_permissions=self._extract_campaign_permissions(),
            budget_limits=self._extract_budget_limits()
        ))
```

#### **2. Negotiation (Aggregate Root)**
```python
class Negotiation(AggregateRoot):
    """
    Proceso de negociación independiente con múltiples rondas.
    """
    def __init__(
        self,
        contract_id: str,
        participants: List[str],
        initial_proposal: Proposal,
        negotiation_id: Optional[str] = None
    ):
        super().__init__(negotiation_id)
        self._contract_id = contract_id
        self._participants = participants
        self._status = NegotiationStatus.ACTIVE
        self._rounds: List[NegotiationRound] = []
        self._deadline: Optional[datetime] = None
        
        # Primera ronda con propuesta inicial
        initial_round = NegotiationRound(
            round_number=1,
            proposal=initial_proposal,
            submitted_by=initial_proposal.submitted_by,
            timestamp=datetime.utcnow()
        )
        self._rounds.append(initial_round)
        
        self.agregar_evento(NegotiationStarted(
            aggregate_id=self.id,
            contract_id=contract_id,
            participants=participants,
            initial_proposal=initial_proposal.to_dict(),
            negotiation_deadline=self._deadline.isoformat() if self._deadline else None
        ))
    
    def submit_proposal(self, proposal: Proposal) -> None:
        """Enviar nueva propuesta en la negociación"""
        if self._status != NegotiationStatus.ACTIVE:
            raise BusinessRuleException("Negotiation is not active")
        
        if proposal.submitted_by not in self._participants:
            raise BusinessRuleException("Submitter not authorized for this negotiation")
        
        if self._deadline and datetime.utcnow() > self._deadline:
            raise BusinessRuleException("Negotiation deadline has passed")
        
        round_number = len(self._rounds) + 1
        new_round = NegotiationRound(
            round_number=round_number,
            proposal=proposal,
            submitted_by=proposal.submitted_by,
            timestamp=datetime.utcnow()
        )
        self._rounds.append(new_round)
        
        self.agregar_evento(ProposalSubmitted(
            aggregate_id=self.id,
            proposal_id=f"{self.id}-round-{round_number}",
            submitted_by=proposal.submitted_by,
            proposal_details=proposal.to_dict(),
            submission_timestamp=new_round.timestamp.isoformat()
        ))
    
    def conclude(self, conclusion_reason: str, concluded_by: str) -> None:
        """Finalizar negociación"""
        if self._status != NegotiationStatus.ACTIVE:
            return
        
        final_proposal = self._rounds[-1].proposal if self._rounds else None
        
        if conclusion_reason == "AGREEMENT" and final_proposal:
            self._status = NegotiationStatus.CONCLUDED_SUCCESS
        else:
            self._status = NegotiationStatus.CONCLUDED_FAILED
        
        self.agregar_evento(NegotiationConcluded(
            aggregate_id=self.id,
            contract_id=self._contract_id,
            final_terms=final_proposal.terms.to_dict() if final_proposal else {},
            conclusion_reason=conclusion_reason,
            concluded_by=concluded_by
        ))
```

### **Value Objects**

#### **ContractTerms**
```python
@dataclass(frozen=True)
class ContractTerms(ValueObject):
    """Términos completos del contrato"""
    
    # Términos financieros
    commission_structure: CommissionStructure
    payment_terms: PaymentTerms
    budget_limits: BudgetLimits
    
    # Términos operacionales
    duration: ContractDuration
    renewal_terms: RenewalTerms
    termination_clauses: TerminationClauses
    
    # Permisos y restricciones
    campaign_permissions: List[str]
    feature_access: List[str]
    geographic_restrictions: List[str]
    
    # SLA y métricas
    sla_terms: SLATerms
    performance_metrics: List[str]
    penalties: List[PenaltyClause]
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.commission_structure:
            raise DomainException("Commission structure is required")
        
        if not self.duration or self.duration.months <= 0:
            raise DomainException("Contract duration must be positive")
        
        if self.budget_limits.monthly_limit <= 0:
            raise DomainException("Budget limits must be positive")
```

#### **ContractStatus**
```python
class ContractStatus(Enum):
    """Estados del contrato con transiciones válidas"""
    DRAFT = "DRAFT"                         # Borrador inicial
    IN_NEGOTIATION = "IN_NEGOTIATION"       # En proceso de negociación  
    LEGAL_REVIEW = "LEGAL_REVIEW"           # Revisión legal pendiente
    PENDING_SIGNATURE = "PENDING_SIGNATURE" # Esperando firmas
    SIGNED = "SIGNED"                       # Firmado por todas las partes
    ACTIVE = "ACTIVE"                       # Contrato activo y vigente
    SUSPENDED = "SUSPENDED"                 # Suspendido temporalmente
    EXPIRED = "EXPIRED"                     # Vencido naturalmente
    TERMINATED = "TERMINATED"               # Terminado anticipadamente
    CANCELLED = "CANCELLED"                 # Cancelado antes de firma
```

---

## 🔄 Comandos y Queries

### **Comandos (Write Side)**

#### **CreateContract**
```python
@dataclass
class CreateContract(Command):
    """Crear nuevo contrato para un partner"""
    partner_id: str
    contract_type: str          # STANDARD, PREMIUM, ENTERPRISE
    template_id: Optional[str]  # Template base para el contrato
    initial_terms: dict         # Términos iniciales propuestos
    created_by: str             # Usuario que crea el contrato
    
    def validate(self) -> None:
        if not self.partner_id:
            raise ValidationException("Partner ID is required")
        if not self.contract_type:
            raise ValidationException("Contract type is required")
        if not self.initial_terms:
            raise ValidationException("Initial terms are required")
```

#### **SignContract**
```python
@dataclass 
class SignContract(Command):
    """Firmar contrato digitalmente"""
    contract_id: str
    signatory_id: str           # ID del firmante
    signature_data: dict        # Datos de la firma digital
    signature_timestamp: str    # Timestamp de la firma
    ip_address: str             # IP desde donde se firmó
    user_agent: str             # User agent del navegador
    
    def validate(self) -> None:
        if not self.contract_id:
            raise ValidationException("Contract ID is required")
        if not self.signatory_id:
            raise ValidationException("Signatory ID is required")
        if not self.signature_data:
            raise ValidationException("Signature data is required")
```

#### **ActivateContract**
```python
@dataclass
class ActivateContract(Command):
    """Activar contrato firmado"""
    contract_id: str
    activation_date: str        # Fecha de activación
    activated_by: str           # Usuario que activa
    activation_notes: Optional[str]  # Notas adicionales
    
    def validate(self) -> None:
        if not self.contract_id:
            raise ValidationException("Contract ID is required")
        
        try:
            datetime.fromisoformat(self.activation_date)
        except ValueError:
            raise ValidationException("Invalid activation date format")
```

### **Queries (Read Side)**

#### **ObtenerContrato**
```python
@dataclass
class ObtenerContrato(Query):
    """Obtener detalles completos de un contrato"""
    contract_id: str
    include_history: bool = False    # Incluir historial de cambios
    include_documents: bool = False  # Incluir documentos asociados
    
class ObtenerContratoResultado:
    def __init__(
        self,
        contract: ContractDTO,
        negotiation_history: Optional[List[NegotiationRoundDTO]] = None,
        documents: Optional[List[DocumentDTO]] = None,
        legal_validations: Optional[List[LegalValidationDTO]] = None
    ):
        self.contract = contract
        self.negotiation_history = negotiation_history or []
        self.documents = documents or []
        self.legal_validations = legal_validations or []
```

#### **ObtenerContratosPorPartner**
```python
@dataclass
class ObtenerContratosPorPartner(Query):
    """Obtener todos los contratos de un partner"""
    partner_id: str
    status_filter: Optional[List[str]] = None  # Filtrar por estados
    date_from: Optional[str] = None            # Fecha desde
    date_to: Optional[str] = None              # Fecha hasta
    limit: int = 50
    offset: int = 0
```

---

## 📡 Integration Events

### **Eventos Entrantes**
```python
# Desde Partner Management
@event_handler('partner-management/partner-registration')
async def on_partner_registration_completed(event: PartnerRegistrationCompleted):
    """Iniciar proceso de contrato cuando partner se registra"""
    
    # Determinar tipo de contrato basado en partner type
    contract_type = determine_contract_type(
        event.partner_type,
        event.registration_data
    )
    
    # Crear comando para nuevo contrato
    command = CreateContract(
        partner_id=event.partner_id,
        contract_type=contract_type,
        initial_terms=generate_initial_terms(event),
        created_by="system"
    )
    
    await self.command_bus.dispatch(command)
```

### **Eventos Salientes**
```python
class ContractActivated(IntegrationEvent):
    """Contrato activado → Multiple services"""
    
    def __init__(self, contract_id: str, partner_id: str, **kwargs):
        super().__init__(
            aggregate_id=contract_id,
            partner_id=partner_id,
            contract_type=kwargs.get('contract_type'),
            effective_date=kwargs.get('effective_date'),
            campaign_permissions=kwargs.get('campaign_permissions', []),
            budget_limits=kwargs.get('budget_limits', {}),
            feature_flags=kwargs.get('feature_flags', {}),
            **kwargs
        )
    
    # Routing a múltiples servicios
    def get_routing_key(self) -> str:
        return f"onboarding.contract.activated.{self.event_data['partner_id']}"
```

---

## 🔒 Business Rules

### **Reglas de Negociación**
```python
class NegotiationMustHaveAuthorizedParticipants(BusinessRule):
    """Solo participantes autorizados pueden negociar"""
    
    def __init__(self, negotiation: Negotiation, participant_id: str):
        self.negotiation = negotiation
        self.participant_id = participant_id
    
    def is_satisfied(self) -> bool:
        return self.participant_id in self.negotiation.participants
    
    def get_message(self) -> str:
        return f"Participant {self.participant_id} not authorized for negotiation"
```

### **Reglas de Firma**
```python
class ContractMustPassLegalValidation(BusinessRule):
    """Contrato debe pasar validación legal antes de firma"""
    
    def __init__(self, contract: Contract):
        self.contract = contract
    
    def is_satisfied(self) -> bool:
        return (
            len(self.contract.legal_validations) > 0 and
            all(v.status == ValidationStatus.APPROVED 
                for v in self.contract.legal_validations)
        )
    
    def get_message(self) -> str:
        return "Contract must pass legal validation before signing"
```

---

## 🗄️ Event Sourcing Implementation

### **Event Store Schema**
```sql
-- Tabla de eventos para contratos
CREATE TABLE contract_events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL DEFAULT 'Contract',
    event_type VARCHAR(200) NOT NULL,
    event_data JSONB NOT NULL,
    event_metadata JSONB NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    sequence_number BIGINT NOT NULL,
    occurred_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    correlation_id UUID,
    causation_id UUID,
    
    CONSTRAINT uk_contract_events_aggregate_sequence 
        UNIQUE (aggregate_id, sequence_number)
);

-- Índices para performance
CREATE INDEX idx_contract_events_aggregate_id ON contract_events (aggregate_id);
CREATE INDEX idx_contract_events_type ON contract_events (event_type);
CREATE INDEX idx_contract_events_occurred ON contract_events (occurred_on);
CREATE INDEX idx_contract_events_correlation ON contract_events (correlation_id);
```

### **Repository Implementation**
```python
class ContractEventSourcedRepository:
    """Repository con Event Sourcing para contratos"""
    
    async def save(self, contract: Contract) -> None:
        """Guardar eventos del contrato"""
        uncommitted_events = contract.obtener_eventos()
        
        if not uncommitted_events:
            return
        
        # Obtener próximo sequence number
        current_version = await self._get_current_version(contract.id)
        
        for i, event in enumerate(uncommitted_events):
            event_record = {
                'aggregate_id': contract.id,
                'aggregate_type': 'Contract',
                'event_type': event.__class__.__name__,
                'event_data': event.to_dict(),
                'event_metadata': {
                    'correlation_id': event.metadata.correlation_id,
                    'causation_id': event.metadata.causation_id,
                    'occurred_on': event.metadata.occurred_on,
                    'event_version': event.metadata.event_version
                },
                'sequence_number': current_version + i + 1,
                'correlation_id': event.metadata.correlation_id
            }
            
            await self.db.execute(
                "INSERT INTO contract_events (...) VALUES (...)",
                event_record
            )
        
        # Limpiar eventos no confirmados
        contract.limpiar_eventos()
    
    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        """Reconstruir contrato desde eventos"""
        events = await self.db.fetch_all(
            "SELECT * FROM contract_events WHERE aggregate_id = $1 ORDER BY sequence_number",
            contract_id
        )
        
        if not events:
            return None
        
        # Reconstruir contrato aplicando eventos en orden
        contract = None
        for event_record in events:
            event = self._deserialize_event(event_record)
            
            if isinstance(event, ContractCreated):
                contract = self._create_contract_from_event(event)
            elif contract:
                contract._apply_event(event)
        
        return contract
```

---

Este diseño del Onboarding Service proporciona una base sólida para la gestión completa del proceso contractual, con trazabilidad total, flexibilidad para negociaciones complejas y integración robusta con los demás servicios del ecosistema HexaBuilders.