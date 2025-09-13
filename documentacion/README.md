# Documentación Arquitectural - HexaBuilders Microservices

Esta documentación contiene el diseño completo de la arquitectura de microservicios para HexaBuilders, incluyendo los 4 servicios principales y sus interacciones.

## 📁 Estructura de la Documentación

### 🏗️ [Arquitectura](./arquitectura/)
- **[OVERVIEW.md](./arquitectura/OVERVIEW.md)** - Visión general del sistema de microservicios
- **[MICROSERVICES_DESIGN.md](./arquitectura/MICROSERVICES_DESIGN.md)** - Diseño detallado de cada servicio
- **[PATTERNS_DECISIONS.md](./arquitectura/PATTERNS_DECISIONS.md)** - Decisiones de patrones y justificaciones técnicas

### 📡 [Eventos](./eventos/)
- **[EVENT_CATALOG.md](./eventos/EVENT_CATALOG.md)** - Catálogo completo de eventos del sistema
- **[INTEGRATION_EVENTS.md](./eventos/INTEGRATION_EVENTS.md)** - Eventos de integración entre servicios
- **[PULSAR_CONFIGURATION.md](./eventos/PULSAR_CONFIGURATION.md)** - Configuración detallada de Apache Pulsar

### 🔧 [Servicios](./servicios/)

#### 📋 [Onboarding Service](./servicios/onboarding/)
- **[SERVICE_DESIGN.md](./servicios/onboarding/SERVICE_DESIGN.md)** - Diseño y arquitectura del servicio
- **[MODULES.md](./servicios/onboarding/MODULES.md)** - Módulos y bounded contexts
- **[EVENTS_COMMANDS.md](./servicios/onboarding/EVENTS_COMMANDS.md)** - Eventos y comandos específicos

#### 👥 [Recruitment Service](./servicios/recruitment/)
- **[SERVICE_DESIGN.md](./servicios/recruitment/SERVICE_DESIGN.md)** - Diseño y arquitectura del servicio
- **[MODULES.md](./servicios/recruitment/MODULES.md)** - Módulos y bounded contexts
- **[EVENTS_COMMANDS.md](./servicios/recruitment/EVENTS_COMMANDS.md)** - Eventos y comandos específicos

#### 📊 [Campaign Management Service](./servicios/campaign_management/)
- **[SERVICE_DESIGN.md](./servicios/campaign_management/SERVICE_DESIGN.md)** - Diseño y arquitectura del servicio
- **[MODULES.md](./servicios/campaign_management/MODULES.md)** - Módulos y bounded contexts
- **[EVENTS_COMMANDS.md](./servicios/campaign_management/EVENTS_COMMANDS.md)** - Eventos y comandos específicos

### 🔗 [Integración](./integracion/)
- **[INTEGRATION_MATRIX.md](./integracion/INTEGRATION_MATRIX.md)** - Matriz de relaciones entre servicios
- **[API_CONTRACTS.md](./integracion/API_CONTRACTS.md)** - Contratos de APIs síncronas
- **[EVENT_FLOWS.md](./integracion/EVENT_FLOWS.md)** - Flujos de eventos por escenario

### 🚀 [Implementación](./implementacion/)
- **[DIRECTORY_STRUCTURE.md](./implementacion/DIRECTORY_STRUCTURE.md)** - Estructura de directorios del proyecto
- **[DOCKER_SETUP.md](./implementacion/DOCKER_SETUP.md)** - Configuración Docker y docker-compose
- **[DEVELOPMENT_GUIDE.md](./implementacion/DEVELOPMENT_GUIDE.md)** - Guía de desarrollo y buenas prácticas

## 🎯 Microservicios del Sistema

| Servicio | Propósito | Patrón de Almacenamiento | Puerto |
|----------|-----------|--------------------------|---------|
| **Partner Management** | Gestión integral de partners | Event Sourcing | 5000 |
| **Onboarding** | Contratos y proceso legal | Event Sourcing | 5001 |
| **Recruitment** | Marketplace de talentos | CRUD Clásico | 5002 |
| **Campaign Management** | Gestión de campañas | Híbrido (CRUD + Event Sourcing) | 5003 |

## 🏛️ Principios Arquitecturales

- **Domain-Driven Design (DDD)**: Cada servicio representa un bounded context
- **CQRS**: Separación de comandos y queries
- **Event-Driven Architecture**: Comunicación asíncrona vía Apache Pulsar
- **Hexagonal Architecture**: Ports & Adapters para desacoplamiento
- **Event Sourcing**: Para servicios que requieren auditoría completa

## 📊 Tecnologías Utilizadas

- **Framework**: Flask (Python)
- **Message Broker**: Apache Pulsar
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker & Docker Compose
- **Serialización**: Avro (Schema Registry)
- **Testing**: pytest

## 🚀 Quick Start

1. **Leer la arquitectura general**: [OVERVIEW.md](./arquitectura/OVERVIEW.md)
2. **Revisar el catálogo de eventos**: [EVENT_CATALOG.md](./eventos/EVENT_CATALOG.md)
3. **Consultar la matriz de integración**: [INTEGRATION_MATRIX.md](./integracion/INTEGRATION_MATRIX.md)
4. **Seguir la guía de desarrollo**: [DEVELOPMENT_GUIDE.md](./implementacion/DEVELOPMENT_GUIDE.md)

---

**Última actualización**: 2025-12-09  
**Versión de la arquitectura**: 2.0  
**Autor**: Equipo de Arquitectura HexaBuilders