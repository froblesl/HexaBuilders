# Estructura de Directorios - HexaBuilders Microservices

## 🎯 Visión General

Esta estructura define la organización completa de código para los 4 microservicios de HexaBuilders, siguiendo principios de Domain-Driven Design (DDD) y Hexagonal Architecture.

---

## 📁 Estructura General del Proyecto

```
HexaBuilders/
├── 📄 README.md                              # Documentación principal
├── 📄 CLAUDE.md                             # Instrucciones para Claude Code
├── 📄 docker-compose.yml                    # Orquestación de servicios
├── 📄 pyproject.toml                        # Configuración del proyecto
├── 📄 requirements.txt                      # Dependencias principales
├── 📄 pulsar-requirements.txt               # Dependencias de Apache Pulsar
├── 
├── 📁 src/                                  # Código fuente principal
│   ├── 📁 partner_management/               # ✅ Servicio existente
│   ├── 📁 onboarding/                       # 🆕 Nuevo servicio
│   ├── 📁 recruitment/                      # 🆕 Nuevo servicio
│   ├── 📁 campaign_management/              # 🆕 Nuevo servicio
│   └── 📁 notificaciones/                   # ✅ Servicio existente
├── 
├── 📁 tests/                                # Tests de todos los servicios
│   ├── 📁 unit/                            # Tests unitarios
│   ├── 📁 integration/                     # Tests de integración
│   └── 📁 e2e/                             # Tests end-to-end
├── 
├── 📁 documentacion/                        # 📚 Documentación arquitectural
│   ├── 📁 arquitectura/
│   ├── 📁 eventos/
│   ├── 📁 servicios/
│   ├── 📁 integracion/
│   └── 📁 implementacion/
├── 
├── 📁 scripts/                              # Scripts de utilidad
│   ├── 📄 setup_environment.py
│   ├── 📄 create_topics.py
│   ├── 📄 migrate_schemas.py
│   └── 📄 health_check.py
├── 
├── 📁 docker/                               # Dockerfiles específicos
│   ├── 📄 partner-management.Dockerfile
│   ├── 📄 onboarding.Dockerfile
│   ├── 📄 recruitment.Dockerfile
│   ├── 📄 campaign-management.Dockerfile
│   └── 📄 notifications.Dockerfile
├── 
├── 📁 k8s/                                  # Manifiestos Kubernetes
│   ├── 📁 base/
│   ├── 📁 environments/
│   └── 📁 monitoring/
└── 
└── 📁 monitoring/                           # Configuración de monitoreo
    ├── 📁 prometheus/
    ├── 📁 grafana/
    └── 📁 alerts/
```

---

## 🏢 Partner Management Service (Existente)

### **Estructura Actual - Mantenida**
```
src/partner_management/
├── 📁 seedwork/                             # Infraestructura compartida
│   ├── 📁 dominio/
│   │   ├── 📄 entidades.py                  # ✅ Entidades base DDD
│   │   ├── 📄 eventos.py                    # ✅ Eventos base
│   │   ├── 📄 excepciones.py                # ✅ Excepciones de dominio
│   │   ├── 📄 fabricas.py                   # ✅ Factory patterns
│   │   ├── 📄 mixins.py                     # ✅ Mixins de dominio
│   │   ├── 📄 objetos_valor.py              # ✅ Value objects base
│   │   ├── 📄 reglas.py                     # ✅ Business rules
│   │   ├── 📄 repositorios.py               # ✅ Repository interfaces
│   │   └── 📄 servicios.py                  # ✅ Domain services
│   ├── 📁 aplicacion/
│   │   ├── 📄 comandos.py                   # ✅ CQRS command framework
│   │   ├── 📄 dto.py                        # ✅ Data transfer objects
│   │   ├── 📄 handlers.py                   # ✅ Command/Query handlers
│   │   ├── 📄 queries.py                    # ✅ Query framework
│   │   └── 📄 servicios.py                  # ✅ Application services
│   ├── 📁 infraestructura/
│   │   ├── 📁 schema/v1/                    # ✅ Avro schemas v1
│   │   ├── 📄 uow.py                        # ✅ Unit of Work
│   │   └── 📄 utils.py                      # ✅ Infrastructure utilities
│   └── 📁 presentacion/
│       └── 📄 api.py                        # ✅ Flask application factory
├── 
├── 📁 modulos/                              # Bounded contexts
│   ├── 📁 partners/                         # ✅ Core partner management
│   ├── 📁 campaigns/                        # ✅ Campaign associations
│   ├── 📁 commissions/                      # ✅ Commission calculations
│   └── 📁 analytics/                        # ✅ Analytics and reporting
└── 
└── 📁 api/
    └── 📄 partners_cqrs.py                  # ✅ CQRS API endpoints
```

---

## 📋 Onboarding Service (Nuevo)

### **Estructura Propuesta**
```
src/onboarding/
├── 📁 seedwork/                             # Compartido con partner_management
│   ├── 📁 dominio/
│   │   ├── 📄 entidades.py                  # Extendido para Event Sourcing
│   │   ├── 📄 eventos.py                    # Eventos específicos onboarding
│   │   └── 📄 excepciones.py                # Excepciones legales/contractuales
│   ├── 📁 aplicacion/
│   │   ├── 📄 comandos.py                   # Comandos específicos onboarding
│   │   ├── 📄 queries.py                    # Queries para reconstrucción
│   │   └── 📄 sagas.py                      # 🆕 Saga patterns para procesos largos
│   ├── 📁 infraestructura/
│   │   ├── 📄 event_store.py                # 🆕 Event Store implementation
│   │   ├── 📄 document_storage.py           # 🆕 Document storage (S3/MinIO)
│   │   └── 📄 external_integrations.py     # 🆕 DocuSign, legal APIs
│   └── 📁 presentacion/
│       ├── 📄 api.py                        # Flask app factory
│       └── 📄 webhooks.py                   # 🆕 Webhooks para servicios externos
├── 
├── 📁 modulos/
│   ├── 📁 contracts/                        # Gestión de contratos
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Contract aggregate root
│   │   │   ├── 📄 objetos_valor.py          # ContractStatus, Terms, etc.
│   │   │   ├── 📄 eventos.py                # Contract domain events
│   │   │   ├── 📄 reglas.py                 # Business rules contractuales
│   │   │   └── 📄 repositorio.py            # Contract repository interface
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 comandos/
│   │   │   │   ├── 📄 crear_contrato.py
│   │   │   │   ├── 📄 actualizar_terminos.py
│   │   │   │   ├── 📄 firmar_contrato.py
│   │   │   │   └── 📄 activar_contrato.py
│   │   │   ├── 📁 queries/
│   │   │   │   ├── 📄 obtener_contrato.py
│   │   │   │   ├── 📄 obtener_historial.py
│   │   │   │   └── 📄 obtener_por_partner.py
│   │   │   ├── 📄 handlers.py               # Command & Query handlers
│   │   │   └── 📄 servicios_aplicacion.py  # Application services
│   │   └── 📁 infraestructura/
│   │       ├── 📄 repositorios_evento.py    # Event sourcing repository
│   │       ├── 📄 dto.py                    # DTOs específicos
│   │       ├── 📄 fabricas.py               # Domain factories
│   │       └── 📁 schema/v1/                # Avro schemas contratos
│   ├── 
│   ├── 📁 negotiations/                     # Proceso de negociación
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Negotiation, Round aggregates
│   │   │   ├── 📄 objetos_valor.py          # Proposal, Terms
│   │   │   └── 📄 eventos.py                # Negotiation events
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 comandos/
│   │   │   └── 📁 queries/
│   │   └── 📁 infraestructura/
│   │       └── 📄 servicios_externos.py     # Email, notifications
│   ├── 
│   ├── 📁 legal/                            # Validación legal
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # LegalValidation, ComplianceCheck
│   │   │   ├── 📄 objetos_valor.py          # ValidationResult, ComplianceStatus
│   │   │   └── 📄 eventos.py                # Legal validation events
│   │   ├── 📁 aplicacion/
│   │   └── 📁 infraestructura/
│   │       ├── 📄 servicios_legales.py      # External legal services
│   │       └── 📄 validadores.py            # Automated validators
│   └── 
│   └── 📁 documents/                        # Gestión documental
│       ├── 📁 dominio/
│       │   ├── 📄 entidades.py              # Document, Signature aggregates
│       │   ├── 📄 objetos_valor.py          # DocumentType, SignatureData
│       │   └── 📄 eventos.py                # Document events
│       ├── 📁 aplicacion/
│       └── 📁 infraestructura/
│           ├── 📄 almacenamiento_docs.py    # S3/MinIO integration
│           └── 📄 servicios_firma.py        # DocuSign integration
└── 
└── 📁 api/
    ├── 📄 contracts_cqrs.py                # Contracts CQRS API
    ├── 📄 negotiations_cqrs.py             # Negotiations API
    ├── 📄 legal_cqrs.py                    # Legal validation API
    └── 📄 documents_cqrs.py                # Document management API
```

---

## 👥 Recruitment Service (Nuevo)

### **Estructura Propuesta**
```
src/recruitment/
├── 📁 seedwork/                             # Compartido, adaptado para CRUD
│   ├── 📁 dominio/
│   │   ├── 📄 entidades.py                  # Entidades CRUD optimizadas
│   │   ├── 📄 eventos.py                    # Eventos de recruitment
│   │   └── 📄 excepciones.py                # Excepciones de matching
│   ├── 📁 aplicacion/
│   │   ├── 📄 comandos.py                   # Comandos CRUD
│   │   ├── 📄 queries.py                    # Queries de búsqueda avanzada
│   │   └── 📄 search_engine.py              # 🆕 ElasticSearch integration
│   ├── 📁 infraestructura/
│   │   ├── 📄 repositorios_crud.py          # 🆕 CRUD repositories
│   │   ├── 📄 search_indexer.py             # 🆕 Search indexing
│   │   └── 📄 ml_services.py                # 🆕 ML for matching
│   └── 📁 presentacion/
│       └── 📄 api.py                        # Flask app con search endpoints
├── 
├── 📁 modulos/
│   ├── 📁 candidates/                       # Gestión de candidatos
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Candidate aggregate root
│   │   │   ├── 📄 objetos_valor.py          # Skills, Experience, Education
│   │   │   ├── 📄 eventos.py                # Candidate events
│   │   │   └── 📄 reglas.py                 # Candidate validation rules
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 comandos/
│   │   │   │   ├── 📄 registrar_candidato.py
│   │   │   │   ├── 📄 actualizar_perfil.py
│   │   │   │   └── 📄 actualizar_skills.py
│   │   │   ├── 📁 queries/
│   │   │   │   ├── 📄 buscar_candidatos.py
│   │   │   │   ├── 📄 obtener_candidato.py
│   │   │   │   └── 📄 obtener_por_skill.py
│   │   │   └── 📄 servicios_aplicacion.py
│   │   └── 📁 infraestructura/
│   │       ├── 📄 repositorios.py           # CRUD repositories
│   │       ├── 📄 search_engine.py          # ElasticSearch integration
│   │       └── 📄 dto.py                    # Search DTOs
│   ├── 
│   ├── 📁 jobs/                             # Ofertas laborales
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Job aggregate root
│   │   │   ├── 📄 objetos_valor.py          # JobRequirements, Salary
│   │   │   └── 📄 eventos.py                # Job events
│   │   ├── 📁 aplicacion/
│   │   └── 📁 infraestructura/
│   ├── 
│   ├── 📁 matching/                         # Algoritmos de matching
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Match, MatchingCriteria
│   │   │   ├── 📄 objetos_valor.py          # MatchScore, MatchReason
│   │   │   ├── 📄 eventos.py                # Matching events
│   │   │   └── 📄 servicios.py              # Matching domain services
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 algoritmos/
│   │   │   │   ├── 📄 skill_matching.py
│   │   │   │   ├── 📄 experience_matching.py
│   │   │   │   └── 📄 composite_matching.py
│   │   │   └── 📁 servicios/
│   │   │       ├── 📄 matching_engine.py
│   │   │       └── 📄 ranking_service.py
│   │   └── 📁 infraestructura/
│   │       ├── 📄 ml_models.py              # ML models para matching
│   │       └── 📄 analytics_service.py      # Matching analytics
│   └── 
│   └── 📁 interviews/                       # Gestión de entrevistas
│       ├── 📁 dominio/
│       │   ├── 📄 entidades.py              # Interview, Feedback
│       │   └── 📄 eventos.py                # Interview events
│       ├── 📁 aplicacion/
│       └── 📁 infraestructura/
│           ├── 📄 calendar_service.py       # Google Calendar
│           └── 📄 video_service.py          # Zoom/Teams integration
└── 
└── 📁 api/
    ├── 📄 candidates_api.py                # Candidates CRUD + Search API
    ├── 📄 jobs_api.py                      # Jobs management API
    ├── 📄 matching_api.py                  # Matching algorithms API
    └── 📄 interviews_api.py                # Interview management API
```

---

## 📊 Campaign Management Service (Nuevo)

### **Estructura Propuesta**
```
src/campaign_management/
├── 📁 seedwork/                             # Híbrido CRUD + Event Sourcing
│   ├── 📁 dominio/
│   │   ├── 📄 entidades.py                  # Entidades híbridas
│   │   ├── 📄 eventos.py                    # Eventos de performance
│   │   └── 📄 excepciones.py                # Excepciones de campaigns
│   ├── 📁 aplicacion/
│   │   ├── 📄 comandos.py                   # Comandos híbridos
│   │   ├── 📄 queries.py                    # Queries tiempo real
│   │   └── 📄 real_time_processor.py       # 🆕 Procesamiento tiempo real
│   ├── 📁 infraestructura/
│   │   ├── 📄 repositorios_crud.py          # CRUD para campaigns
│   │   ├── 📄 event_store_metrics.py       # Event sourcing para métricas
│   │   ├── 📄 time_series_db.py            # InfluxDB para time series
│   │   └── 📄 external_apis.py             # Facebook/Google Ads APIs
│   └── 📁 presentacion/
│       ├── 📄 api.py                        # Flask app factory
│       └── 📁 websockets/
│           └── 📄 real_time_metrics.py     # 🆕 WebSocket real-time updates
├── 
├── 📁 modulos/
│   ├── 📁 campaigns/                        # Gestión de campañas
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Campaign aggregate root
│   │   │   ├── 📄 objetos_valor.py          # CampaignType, Status, Goals
│   │   │   ├── 📄 eventos.py                # Campaign events
│   │   │   └── 📄 reglas.py                 # Campaign business rules
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 comandos/
│   │   │   │   ├── 📄 crear_campaign.py
│   │   │   │   ├── 📄 lanzar_campaign.py
│   │   │   │   ├── 📄 pausar_campaign.py
│   │   │   │   └── 📄 completar_campaign.py
│   │   │   ├── 📁 queries/
│   │   │   │   ├── 📄 obtener_campaign.py
│   │   │   │   ├── 📄 obtener_metricas.py
│   │   │   │   └── 📄 dashboard_partner.py
│   │   │   └── 📄 servicios_aplicacion.py
│   │   └── 📁 infraestructura/
│   │       ├── 📄 repositorios_crud.py      # CRUD repositories
│   │       └── 📄 servicios_externos.py     # Ad platform integrations
│   ├── 
│   ├── 📁 targeting/                        # Segmentación de audiencias
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Audience, Segment
│   │   │   ├── 📄 objetos_valor.py          # Demographics, Interests
│   │   │   └── 📄 servicios.py              # Targeting domain services
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 algoritmos/
│   │   │   │   ├── 📄 lookalike_modeling.py
│   │   │   │   └── 📄 behavioral_clustering.py
│   │   │   └── 📁 servicios/
│   │   │       └── 📄 targeting_optimizer.py
│   │   └── 📁 infraestructura/
│   │       └── 📄 ml_models.py              # ML models para targeting
│   ├── 
│   ├── 📁 performance/                      # Métricas en tiempo real
│   │   ├── 📁 dominio/
│   │   │   ├── 📄 entidades.py              # Metric, KPI (Event Sourced)
│   │   │   ├── 📄 objetos_valor.py          # MetricValue, Threshold
│   │   │   ├── 📄 eventos.py                # Performance events
│   │   │   └── 📄 servicios.py              # Performance services
│   │   ├── 📁 aplicacion/
│   │   │   ├── 📁 real_time/
│   │   │   │   ├── 📄 metrics_processor.py
│   │   │   │   ├── 📄 streaming_aggregator.py
│   │   │   │   └── 📄 alert_engine.py
│   │   │   └── 📁 servicios/
│   │   │       └── 📄 anomaly_detector.py
│   │   └── 📁 infraestructura/
│   │       ├── 📄 event_store_metrics.py    # Event sourcing
│   │       ├── 📄 time_series_db.py         # InfluxDB
│   │       └── 📄 streaming_platform.py     # Kafka/Pulsar
│   └── 
│   └── 📁 budgets/                          # Control presupuestario
│       ├── 📁 dominio/
│       │   ├── 📄 entidades.py              # Budget, Allocation
│       │   ├── 📄 objetos_valor.py          # BudgetLimit, SpendRate
│       │   ├── 📄 eventos.py                # Budget events
│       │   └── 📄 reglas.py                 # Budget business rules
│       ├── 📁 aplicacion/
│       │   └── 📁 servicios/
│       │       ├── 📄 budget_optimizer.py
│       │       └── 📄 spend_forecaster.py
│       └── 📁 infraestructura/
│           └── 📄 payment_gateways.py       # Stripe, PayPal
└── 
└── 📁 api/
    ├── 📄 campaigns_api.py                 # Campaigns CRUD API
    ├── 📄 targeting_api.py                 # Targeting configuration API
    ├── 📄 performance_api.py               # Real-time performance API
    └── 📄 budgets_api.py                   # Budget management API
```

---

## 📧 Notifications Service (Existente - Evolucionado)

### **Estructura Actual Mejorada**
```
src/notificaciones/
├── 📄 __init__.py                          # ✅ Existente
├── 📄 main.py                              # ✅ Entry point existente
├── 
├── 📁 dominio/                              # 🆕 Agregar estructura DDD
│   ├── 📄 entidades.py                      # Notification, Template
│   ├── 📄 objetos_valor.py                  # NotificationType, Channel
│   └── 📄 eventos.py                        # Notification events
├── 
├── 📁 aplicacion/                           # 🆕 Application layer
│   ├── 📁 comandos/
│   │   ├── 📄 enviar_notificacion.py
│   │   └── 📄 crear_template.py
│   ├── 📁 queries/
│   │   └── 📄 obtener_historial.py
│   └── 📄 servicios_aplicacion.py
├── 
├── 📁 infraestructura/                      # 🆕 Infrastructure layer
│   ├── 📄 email_service.py                  # SendGrid, SMTP
│   ├── 📄 sms_service.py                    # Twilio, AWS SNS
│   ├── 📄 push_service.py                   # Firebase, Apple Push
│   └── 📄 template_engine.py                # Jinja2 templates
└── 
└── 📁 api/                                  # 🆕 REST API
    └── 📄 notifications_api.py              # Notification management API
```

---

## 🧪 Testing Structure

### **Estructura de Tests**
```
tests/
├── 📁 unit/                                # Tests unitarios por servicio
│   ├── 📁 partner_management/
│   │   ├── 📁 modulos/
│   │   │   ├── 📁 partners/
│   │   │   │   ├── 📁 dominio/
│   │   │   │   ├── 📁 aplicacion/
│   │   │   │   └── 📁 infraestructura/
│   │   │   ├── 📁 campaigns/
│   │   │   ├── 📁 commissions/
│   │   │   └── 📁 analytics/
│   │   └── 📁 seedwork/
│   ├── 📁 onboarding/
│   │   ├── 📁 modulos/
│   │   │   ├── 📁 contracts/
│   │   │   ├── 📁 negotiations/
│   │   │   ├── 📁 legal/
│   │   │   └── 📁 documents/
│   │   └── 📁 seedwork/
│   ├── 📁 recruitment/
│   │   ├── 📁 modulos/
│   │   │   ├── 📁 candidates/
│   │   │   ├── 📁 jobs/
│   │   │   ├── 📁 matching/
│   │   │   └── 📁 interviews/
│   │   └── 📁 seedwork/
│   ├── 📁 campaign_management/
│   │   ├── 📁 modulos/
│   │   │   ├── 📁 campaigns/
│   │   │   ├── 📁 targeting/
│   │   │   ├── 📁 performance/
│   │   │   └── 📁 budgets/
│   │   └── 📁 seedwork/
│   └── 📁 notificaciones/
├── 
├── 📁 integration/                          # Tests de integración
│   ├── 📁 event_flows/
│   │   ├── 📄 test_onboarding_flow.py
│   │   ├── 📄 test_recruitment_flow.py
│   │   └── 📄 test_campaign_flow.py
│   ├── 📁 api_integration/
│   │   ├── 📄 test_partner_management_api.py
│   │   ├── 📄 test_onboarding_api.py
│   │   ├── 📄 test_recruitment_api.py
│   │   └── 📄 test_campaign_management_api.py
│   └── 📁 database/
│       ├── 📄 test_repositories.py
│       └── 📄 test_event_store.py
├── 
├── 📁 e2e/                                  # Tests end-to-end
│   ├── 📄 test_complete_onboarding.py
│   ├── 📄 test_recruitment_process.py
│   ├── 📄 test_campaign_lifecycle.py
│   └── 📄 test_contract_renewal.py
├── 
├── 📁 performance/                          # Tests de rendimiento
│   ├── 📄 test_event_throughput.py
│   ├── 📄 test_api_latency.py
│   └── 📄 test_search_performance.py
├── 
└── 📁 fixtures/                             # Datos de prueba
    ├── 📁 events/
    ├── 📁 contracts/
    ├── 📁 candidates/
    └── 📁 campaigns/
```

---

## 🔧 Configuration Structure

### **Configuración por Ambiente**
```
config/
├── 📁 environments/
│   ├── 📄 development.yml
│   ├── 📄 staging.yml
│   ├── 📄 production.yml
│   └── 📄 testing.yml
├── 
├── 📁 services/
│   ├── 📄 partner_management.yml
│   ├── 📄 onboarding.yml
│   ├── 📄 recruitment.yml
│   ├── 📄 campaign_management.yml
│   └── 📄 notifications.yml
├── 
├── 📁 infrastructure/
│   ├── 📄 pulsar.yml
│   ├── 📄 postgresql.yml
│   ├── 📄 elasticsearch.yml
│   └── 📄 redis.yml
└── 
└── 📁 schemas/
    ├── 📁 avro/
    │   ├── 📁 v1/
    │   └── 📁 v2/
    └── 📁 openapi/
        ├── 📄 partner_management.yml
        ├── 📄 onboarding.yml
        ├── 📄 recruitment.yml
        └── 📄 campaign_management.yml
```

---

## 📦 Docker Structure

### **Dockerfiles Específicos**
```
docker/
├── 📄 partner-management.Dockerfile        # ✅ Existente
├── 📄 onboarding.Dockerfile                # 🆕 Event Sourcing optimizado
├── 📄 recruitment.Dockerfile               # 🆕 Con ElasticSearch
├── 📄 campaign-management.Dockerfile       # 🆕 Híbrido con time series
├── 📄 notifications.Dockerfile             # ✅ Existente mejorado
├── 
├── 📁 base/
│   ├── 📄 python-base.Dockerfile           # Base image compartida
│   └── 📄 python-ml.Dockerfile             # Base con ML libraries
├── 
└── 📁 compose/
    ├── 📄 docker-compose.yml               # ✅ Configuración principal
    ├── 📄 docker-compose.override.yml      # Development overrides
    ├── 📄 docker-compose.prod.yml          # Production specific
    └── 📄 docker-compose.test.yml          # Testing environment
```

---

Esta estructura proporciona una organización clara, escalable y mantenible para el ecosistema completo de microservicios HexaBuilders, siguiendo las mejores prácticas de DDD, separación de responsabilidades y principios SOLID.