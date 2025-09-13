# Visión General de la Arquitectura - HexaBuilders Microservices

## 🎯 Introducción

HexaBuilders evoluciona de un sistema monolítico de gestión de partners hacia una **arquitectura de microservicios basada en eventos**, diseñada para soportar el crecimiento empresarial y la escalabilidad horizontal.

## 🏗️ Arquitectura de Alto Nivel

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Partner Mgmt   │    │   Onboarding    │    │   Recruitment   │    │ Campaign Mgmt   │
│     (5000)      │    │     (5001)      │    │     (5002)      │    │     (5003)      │
│                 │    │                 │    │                 │    │                 │
│ Event Sourcing  │    │ Event Sourcing  │    │  CRUD Classic   │    │    Hybrid       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │                      │
          └──────────────────────┼──────────────────────┼──────────────────────┘
                                 │                      │
                    ┌────────────▼──────────────────────▼────────────┐
                    │            Apache Pulsar Cluster               │
                    │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
                    │  │ZooKeeper │ │  Broker  │ │ Schema Reg.  │   │
                    │  └──────────┘ └──────────┘ └──────────────┘   │
                    └─────────────────────────────────────────────────┘
                                             │
                    ┌─────────────────────────────────────────────────┐
                    │              PostgreSQL Database                │
                    │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
                    │  │Partners  │ │Contracts │ │ Candidates   │   │
                    │  └──────────┘ └──────────┘ └──────────────┘   │
                    └─────────────────────────────────────────────────┘
```

## 🔧 Microservicios Principales

### 1. **Partner Management Service** (Puerto 5000)
**Contexto**: Gestión integral de partners y relaciones comerciales

**Responsabilidades**:
- 🏢 Registro y onboarding de partners
- 👤 Perfiles 360° completos
- 📊 Métricas y analytics de rendimiento
- 🔄 Gestión de estados y validaciones

**Módulos**:
- `partners/` - Gestión de partners
- `campaigns/` - Campañas asociadas
- `commissions/` - Comisiones y pagos
- `analytics/` - Métricas y reportes

### 2. **Onboarding Service** (Puerto 5001)
**Contexto**: Gestión del proceso legal y contractual

**Responsabilidades**:
- 📄 Gestión de contratos y términos legales
- 🤝 Proceso de negociación
- ⚖️ Validación legal y compliance
- 📋 Documentación y firmas digitales

**Módulos**:
- `contracts/` - Contratos y términos
- `negotiations/` - Proceso de negociación
- `legal/` - Validación legal
- `documents/` - Gestión documental

### 3. **Recruitment Service** (Puerto 5002)
**Contexto**: Marketplace de talentos y reclutamiento

**Responsabilidades**:
- 👥 Gestión de candidatos y perfiles
- 💼 Ofertas laborales y requisitos
- 🎯 Matching inteligente candidato-trabajo
- 📞 Proceso de entrevistas

**Módulos**:
- `candidates/` - Perfiles de candidatos
- `jobs/` - Ofertas laborales
- `matching/` - Algoritmos de matching
- `interviews/` - Gestión de entrevistas

### 4. **Campaign Management Service** (Puerto 5003)
**Contexto**: Gestión avanzada de campañas de marketing

**Responsabilidades**:
- 🎯 Ciclo de vida completo de campañas
- 📊 Segmentación y targeting avanzado
- 📈 Métricas en tiempo real
- 💰 Control presupuestario inteligente

**Módulos**:
- `campaigns/` - Gestión de campañas
- `targeting/` - Segmentación de audiencias
- `performance/` - Métricas y KPIs
- `budgets/` - Control presupuestario

## 🎨 Patrones Arquitecturales Implementados

### **Domain-Driven Design (DDD)**
```
Bounded Context = Microservicio
├── Domain Layer (Entidades, Value Objects, Eventos)
├── Application Layer (Casos de Uso, Comandos, Queries)
├── Infrastructure Layer (Repositorios, Adaptadores)
└── Presentation Layer (APIs REST, Controllers)
```

### **CQRS (Command Query Responsibility Segregation)**
```
Write Side (Comandos)          Read Side (Queries)
┌─────────────────┐           ┌─────────────────┐
│ HTTP POST/PUT   │──────────▶│ HTTP GET        │
│ Returns 202     │           │ Returns 200+data│
│ Async Process   │           │ Sync Response   │
└─────────────────┘           └─────────────────┘
```

### **Event-Driven Architecture**
```
Service A ──[Command]──▶ Service B ──[Event]──▶ Service C
    │                        │                     │
    └──[Integration Event]───┴──[Domain Event]────┘
                             │
                      ┌──────▼──────┐
                      │Apache Pulsar│
                      └─────────────┘
```

### **Hexagonal Architecture (Ports & Adapters)**
```
          ┌─────────────────────────┐
          │       Domain            │
          │   ┌─────────────────┐   │
          │   │   Entities      │   │
          │   │   Events        │   │
          │   │   Rules         │   │
          │   └─────────────────┘   │
          └─────────┬───────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐       ┌───▼───┐       ┌───▼───┐
│  API  │       │  DB   │       │ MSG   │
│Adapter│       │Adapter│       │Adapter│
└───────┘       └───────┘       └───────┘
```

## 📊 Decisiones de Almacenamiento

| Servicio | Patrón | Justificación |
|----------|--------|---------------|
| **Partner Management** | Event Sourcing | ✅ Ya implementado, requiere auditoría completa |
| **Onboarding** | Event Sourcing | ⚖️ Contratos legales requieren trazabilidad total |
| **Recruitment** | CRUD | 🔍 Búsquedas complejas y filtros de candidatos |
| **Campaign Management** | Híbrido | 📊 Queries frecuentes + auditoría de métricas |

## 🚀 Comunicación Entre Servicios

### **Asíncrona (Apache Pulsar)**
- ✅ **Integration Events**: Comunicación entre bounded contexts
- ✅ **Domain Events**: Comunicación interna del servicio
- ✅ **Schema Versioning**: Evolución de esquemas con Avro

### **Síncrona (HTTP/gRPC)**
- ✅ **Queries de solo lectura**: Datos en tiempo real
- ✅ **APIs públicas**: Interfaces de usuario
- ✅ **Health checks**: Monitoreo y observabilidad

## 🔒 Principios de Seguridad y Calidad

### **Resilencia**
- Circuit Breakers para servicios externos
- Retry patterns con backoff exponencial
- Dead Letter Queues para eventos fallidos

### **Observabilidad**
- Correlation IDs para trazabilidad end-to-end
- Métricas de negocio y técnicas
- Logging estructurado con contexto

### **Escalabilidad**
- Particionado de topics por tenant
- Load balancing automático
- Horizontal scaling ready

## 📈 Beneficios de la Arquitectura

### **Técnicos**
- 🔧 **Mantenibilidad**: Cada servicio es independiente
- ⚡ **Rendimiento**: Optimización específica por dominio
- 🔄 **Escalabilidad**: Scaling independiente por necesidad
- 🛡️ **Resilencia**: Failure isolation entre servicios

### **De Negocio**
- 🚀 **Time to Market**: Despliegues independientes
- 👥 **Team Autonomy**: Equipos especializados por dominio
- 💡 **Innovación**: Tecnologías específicas por servicio
- 📊 **Analytics**: Insights granulares por contexto

## 🎯 Roadmap de Migración

### **Fase 1** (Actual)
- ✅ Partner Management Service (Completado)

### **Fase 2** (Próxima)
- 🔄 Onboarding Service
- 🔄 Recruitment Service  
- 🔄 Campaign Management Service

### **Fase 3** (Futuro)
- 📧 Notifications Service (Evolution)
- 🔍 Search & Discovery Service
- 📊 Advanced Analytics Service

---

Esta arquitectura establece las bases para un sistema escalable, mantenible y orientado al futuro del negocio de HexaBuilders.