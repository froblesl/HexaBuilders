# Decisiones de Patrones Arquitecturales - HexaBuilders

## 🎯 Filosofía de Diseño

La arquitectura de HexaBuilders se basa en principios probados de ingeniería de software empresarial, priorizando:

- **Separación de responsabilidades** clara entre contextos de negocio
- **Evolución independiente** de cada microservicio
- **Resilencia y tolerancia a fallos** mediante event-driven patterns
- **Auditoría y trazabilidad** completa de operaciones críticas
- **Escalabilidad horizontal** sin límites arquitecturales

---

## 📊 Matriz de Decisiones de Almacenamiento

| Servicio | Patrón Elegido | Justificación Técnica | Justificación de Negocio |
|----------|----------------|----------------------|--------------------------|
| **Partner Management** | Event Sourcing | ✅ Ya implementado<br>📊 Auditoría completa<br>🔄 Reconstrucción de estado | 📈 Métricas históricas<br>⚖️ Compliance regulatorio<br>🔍 Debug de comportamiento |
| **Onboarding** | Event Sourcing | ⚖️ Trazabilidad legal total<br>📋 Historial de negociación<br>🔒 Integridad contractual | 🏛️ Requisitos legales<br>📑 Auditoría contractual<br>⏱️ Reconstrucción temporal |
| **Recruitment** | CRUD Clásico | 🔍 Búsquedas complejas<br>📊 Queries de agregación<br>⚡ Performance optimizada | 🎯 Matching en tiempo real<br>🔎 Filtros avanzados<br>📱 UX responsiva |
| **Campaign Management** | Híbrido | 📈 Métricas (Event Sourcing)<br>🎯 Campañas (CRUD)<br>⚖️ Balance rendimiento/auditoría | 📊 Analytics históricos<br>⚡ Dashboard real-time<br>💰 Control presupuestario |

---

## 🏗️ Patrones Arquitecturales Implementados

### **1. Domain-Driven Design (DDD)**

#### **Decisión**: Bounded Context per Microservice
```
Business Domain: Partner Ecosystem Management
├── Partner Management BC    → Microservice
├── Onboarding BC           → Microservice  
├── Recruitment BC          → Microservice
└── Campaign Management BC  → Microservice
```

#### **Justificación**:
- ✅ **Cohesión alta**: Cada servicio maneja conceptos relacionados
- ✅ **Acoplamiento bajo**: Interfaces claras entre contextos
- ✅ **Evolución independiente**: Equipos especializados por dominio
- ✅ **Lenguaje ubicuo**: Terminología consistente por contexto

#### **Implementación**:
```python
# Cada bounded context tiene su propio modelo
class Partner(AggregateRoot):  # Partner Management
    pass

class Contract(AggregateRoot): # Onboarding  
    pass

class Candidate(AggregateRoot): # Recruitment
    pass

class Campaign(AggregateRoot): # Campaign Management
    pass
```

---

### **2. CQRS (Command Query Responsibility Segregation)**

#### **Decisión**: Separación completa Read/Write en todos los servicios

#### **Command Side (Write)**:
```python
# Operaciones de escritura - Asíncronas
@bp.route('/partners-comando', methods=['POST'])
def crear_partner_comando():
    comando = CrearPartner(...)
    partner_id = ejecutar_comando(comando)
    return Response(status=202, headers={'Location': f'/partners-query/{partner_id}'})
```

#### **Query Side (Read)**:
```python
# Operaciones de lectura - Síncronas
@bp.route('/partners-query/<partner_id>', methods=['GET'])
def obtener_partner_query(partner_id):
    query = ObtenerPartner(partner_id=partner_id)
    resultado = ejecutar_query(query)
    return jsonify(resultado.partner.to_dict()), 200
```

#### **Justificación**:
- ⚡ **Performance**: Optimización independiente de read/write
- 🔄 **Scalability**: Scaling horizontal diferenciado
- 🧹 **Separation of Concerns**: Modelos optimizados por uso
- 📊 **Analytics**: Proyecciones especializadas para reportes

---

### **3. Event-Driven Architecture**

#### **Decisión**: Apache Pulsar como Event Backbone

#### **Tipos de Eventos**:

##### **Domain Events (Internos)**
```python
class PartnerCreated(DomainEvent):
    """Evento interno al servicio Partner Management"""
    def __init__(self, aggregate_id: str, business_name: str, email: str):
        super().__init__(
            aggregate_id=aggregate_id,
            business_name=business_name,
            email=email
        )
```

##### **Integration Events (Entre servicios)**
```python
class PartnerRegistrationCompleted(IntegrationEvent):
    """Evento entre Partner Management → Onboarding"""
    def to_cloud_event(self) -> Dict[str, Any]:
        return {
            'specversion': '1.0',
            'type': 'com.hexabuilders.partners.PartnerRegistrationCompleted',
            'source': f'//partners/{self.aggregate_id}',
            'data': self.event_data
        }
```

#### **Justificación**:
- 🔄 **Decoupling**: Servicios no se conocen directamente
- 📈 **Scalability**: Procesamiento asíncrono de carga
- 🛡️ **Resilience**: Tolerancia a fallos de servicios individuales
- 📊 **Auditability**: Trazabilidad completa de interacciones

---

### **4. Event Sourcing vs CRUD**

#### **Event Sourcing** (Partner Management, Onboarding)

##### **Implementación**:
```python
class PartnerEventStore:
    def save_events(self, aggregate_id: str, events: List[DomainEvent]):
        for event in events:
            event_record = EventRecord(
                aggregate_id=aggregate_id,
                event_type=event.__class__.__name__,
                event_data=event.to_dict(),
                version=self._get_next_version(aggregate_id),
                timestamp=datetime.utcnow()
            )
            self.db.save(event_record)
    
    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        records = self.db.query(aggregate_id)
        return [self._deserialize_event(record) for record in records]
```

##### **Reconstrucción de Estado**:
```python
def reconstruct_partner(partner_id: str) -> Partner:
    events = event_store.get_events(partner_id)
    partner = None
    
    for event in events:
        if isinstance(event, PartnerCreated):
            partner = Partner.from_creation_event(event)
        elif isinstance(event, PartnerStatusChanged):
            partner.apply_status_change(event)
        # ... más eventos
    
    return partner
```

#### **CRUD Clásico** (Recruitment)

##### **Implementación**:
```python
class CandidateRepository:
    def save(self, candidate: Candidate):
        candidate_data = CandidateDTO.from_entity(candidate)
        self.db.session.merge(candidate_data)
        self.db.session.commit()
    
    def find_by_skills(self, skills: List[str]) -> List[Candidate]:
        return self.db.session.query(CandidateDTO)\
            .join(SkillDTO)\
            .filter(SkillDTO.name.in_(skills))\
            .all()
```

#### **Híbrido** (Campaign Management)

##### **Campañas → CRUD**:
```python
class CampaignRepository:
    def find_active_campaigns(self, partner_id: str) -> List[Campaign]:
        return self.db.session.query(CampaignDTO)\
            .filter(CampaignDTO.partner_id == partner_id)\
            .filter(CampaignDTO.status == CampaignStatus.ACTIVE)\
            .all()
```

##### **Métricas → Event Sourcing**:
```python
class MetricsEventStore:
    def record_metric_update(self, campaign_id: str, metric: MetricUpdated):
        # Almacenar como evento para auditoría y reconstrucción
        pass
    
    def get_metrics_history(self, campaign_id: str, period: DateRange):
        # Reconstruir métricas históricas desde eventos
        pass
```

---

### **5. Hexagonal Architecture (Ports & Adapters)**

#### **Decisión**: Separación clara de capas en cada servicio

```
┌─────────────────────────────────────────────────┐
│                 Domain Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │  Entities   │ │Value Objects│ │   Events  │  │
│  └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────┬───────────────────────────────┘
                  │ (Ports - Interfaces)
┌─────────────────▼───────────────────────────────┐
│               Application Layer                 │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │  Commands   │ │   Queries   │ │ Handlers  │  │
│  └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────┬───────────────────────────────┘
                  │ (Adapters - Implementations)
┌─────────────────▼───────────────────────────────┐
│             Infrastructure Layer                │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │ Repositories│ │  Message    │ │    API    │  │
│  │             │ │   Broker    │ │ Adapters  │  │
│  └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────────────────────────────────────┘
```

#### **Implementación de Ports**:
```python
# Domain Layer - Port (Interface)
class PartnerRepository(ABC):
    @abstractmethod
    def save(self, partner: Partner) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, partner_id: str) -> Optional[Partner]:
        pass

# Infrastructure Layer - Adapter (Implementation)
class PostgreSQLPartnerRepository(PartnerRepository):
    def save(self, partner: Partner) -> None:
        # Implementación específica para PostgreSQL
        pass
    
    def find_by_id(self, partner_id: str) -> Optional[Partner]:
        # Implementación específica para PostgreSQL
        pass
```

---

### **6. Schema Evolution con Apache Pulsar**

#### **Decisión**: Versionado de esquemas con Avro

#### **Schema Registry**:
```python
# Schema v1
PARTNER_CREATED_SCHEMA_V1 = {
    "type": "record",
    "name": "PartnerCreatedEvent",
    "namespace": "com.hexabuilders.partners.events.v1",
    "fields": [
        {"name": "partner_id", "type": "string"},
        {"name": "business_name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "partner_type", "type": "string"}
    ]
}

# Schema v2 - Evolutivo (Añade campo opcional)
PARTNER_CREATED_SCHEMA_V2 = {
    "type": "record",
    "name": "PartnerCreatedEvent", 
    "namespace": "com.hexabuilders.partners.events.v2",
    "fields": [
        {"name": "partner_id", "type": "string"},
        {"name": "business_name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "partner_type", "type": "string"},
        {"name": "registration_source", "type": ["null", "string"], "default": null}
    ]
}
```

#### **Compatibilidad hacia atrás**:
```python
class EventVersionCompatibility:
    def deserialize_event(self, event_data: bytes, target_version: int):
        current_version = self.detect_version(event_data)
        
        if current_version < target_version:
            # Migrar hacia adelante
            return self.migrate_forward(event_data, current_version, target_version)
        elif current_version > target_version:
            # Compatibilidad hacia atrás
            return self.downgrade_event(event_data, current_version, target_version)
        
        return self.deserialize_direct(event_data)
```

---

### **7. Resilience Patterns**

#### **Circuit Breaker**
```python
class ServiceCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    async def call(self, service_call):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenException()
        
        try:
            result = await service_call()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

#### **Retry with Exponential Backoff**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(TransientException)
)
async def publish_integration_event(event: IntegrationEvent):
    try:
        await pulsar_client.publish(event.to_cloud_event())
    except PulsarConnectionException:
        # Se reintentará automáticamente
        raise TransientException("Pulsar connection failed")
```

---

### **8. Observability Patterns**

#### **Correlation ID Tracing**
```python
class CorrelationIdMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        correlation_id = environ.get('HTTP_X_CORRELATION_ID') or str(uuid.uuid4())
        
        # Propagar a todos los logs y eventos
        with correlation_context(correlation_id):
            return self.app(environ, start_response)

@event_handler
def on_partner_created(event: PartnerCreated):
    logger.info(
        f"Processing PartnerCreated event",
        extra={
            'correlation_id': get_current_correlation_id(),
            'event_id': event.metadata.event_id,
            'partner_id': event.aggregate_id
        }
    )
```

#### **Structured Logging**
```python
class StructuredLogger:
    def log_command_execution(self, command: Command, result: CommandResult):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'command_executed',
            'command_type': command.__class__.__name__,
            'command_id': command.command_id,
            'correlation_id': command.correlation_id,
            'success': result.success,
            'execution_time_ms': result.execution_time_ms,
            'service': 'partner-management'
        }
        
        if result.success:
            logger.info("Command executed successfully", extra=log_entry)
        else:
            log_entry['error'] = result.error
            logger.error("Command execution failed", extra=log_entry)
```

---

## 📈 Beneficios de las Decisiones Tomadas

### **Técnicos**
- 🔧 **Mantenibilidad**: Separación clara de responsabilidades
- ⚡ **Performance**: Optimización específica por patrón de uso
- 🔄 **Scalability**: Scaling independiente por servicio
- 🛡️ **Resilience**: Aislamiento de fallos entre contextos
- 🔍 **Debuggability**: Trazabilidad completa de operaciones

### **De Negocio**
- 🚀 **Time to Market**: Desarrollo y despliegue independiente
- 👥 **Team Autonomy**: Equipos especializados por dominio
- 💡 **Innovation**: Tecnologías apropiadas por contexto
- 📊 **Compliance**: Auditoría y trazabilidad reglamentaria
- 💰 **Cost Optimization**: Recursos específicos por necesidad

### **Operacionales**
- 📊 **Observability**: Métricas y logs estructurados
- 🔄 **Deployment**: CI/CD independiente por servicio
- 📈 **Monitoring**: KPIs específicos por contexto
- 🔒 **Security**: Aislamiento de datos sensibles
- 🌍 **Multi-tenancy**: Escalabilidad empresarial

---

Estas decisiones arquitecturales proporcionan una base sólida para el crecimiento futuro de HexaBuilders, balanceando complejidad técnica con beneficios de negocio y mantenibilidad a largo plazo.