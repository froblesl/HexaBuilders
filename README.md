# HexaBuilders - Microservices Platform

A microservices system built with Domain-Driven Design (DDD), Event-Driven Architecture, and the Saga pattern for distributed transactions.

## 🏗️ Architecture Overview

HexaBuilders is a comprehensive microservices platform that implements:

- **Microservices Architecture** with Domain-Driven Design
- **Event-Driven Architecture** using Apache Pulsar
- **Saga Pattern** for distributed transactions (Choreography-based)
- **CQRS** (Command Query Responsibility Segregation)
- **Hexagonal Architecture** (Ports & Adapters)
- **Backend for Frontend (BFF)** with GraphQL
- **Kubernetes** deployment ready

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Kubernetes cluster (for production)
- Google Cloud Platform account (for GKE deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HexaBuilders-1
   ```

2. **Start the platform**
   ```bash
   docker-compose up -d
   ```

3. **Access the services**
   - BFF Web (GraphQL): http://localhost:8000
   - Partner Management: http://localhost:5000
   - Onboarding: http://localhost:5001
   - Recruitment: http://localhost:5002
   - Campaign Management: http://localhost:5003
   - Notifications: http://localhost:5004

### Production Deployment

1. **Create GKE cluster**
   ```bash
   ./scripts/create-gke-cluster.sh YOUR_PROJECT_ID
   ```

2. **Build and push images**
   ```bash
   ./scripts/build-and-push-images.sh YOUR_PROJECT_ID v1.0.0
   ```

3. **Deploy to Kubernetes**
   ```bash
   ./scripts/deploy-to-gke.sh YOUR_PROJECT_ID
   ```

## 📁 Project Structure

```
HexaBuilders-1/
├── src/                          # Source code
│   ├── bff_web/                  # Backend for Frontend (GraphQL)
│   ├── partner_management/       # Partner Management Service
│   ├── onboarding/               # Onboarding Service
│   ├── recruitment/              # Recruitment Service
│   ├── campaign_management/      # Campaign Management Service
│   ├── notificaciones/           # Notifications Service
│   └── pulsar_event_dispatcher.py # Event dispatcher
├── k8s/                          # Kubernetes deployments
├── dockerfiles/                  # Docker files
├── scripts/                      # Deployment scripts
├── tests/                        # Test suites
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── scripts/                  # Test scripts
├── documentacion/                # Documentation
│   ├── arquitectura/             # Architecture docs
│   ├── implementacion/           # Implementation guides
│   ├── eventos/                  # Event documentation
│   └── servicios/                # Service documentation
├── postman/                      # API collections
└── sql/                          # Database scripts
```

## Core Services

### Partner Management
- **Port**: 5000
- **Purpose**: Manages partner lifecycle and onboarding
- **Key Features**: CQRS, Domain Events, Saga Orchestration

### Onboarding
- **Port**: 5001
- **Purpose**: Handles partner onboarding process
- **Key Features**: Contract management, Document verification

### Recruitment
- **Port**: 5002
- **Purpose**: Manages job postings and candidate matching
- **Key Features**: Elasticsearch integration, Advanced search

### Campaign Management
- **Port**: 5003
- **Purpose**: Handles marketing campaigns
- **Key Features**: Performance tracking, Budget management

### Notifications
- **Port**: 5004
- **Purpose**: Sends notifications across the platform
- **Key Features**: Multi-channel notifications

### BFF Web (GraphQL)
- **Port**: 8000
- **Purpose**: Backend for Frontend with GraphQL API
- **Key Features**: Single endpoint, Real-time subscriptions

## Event-Driven Architecture

The platform uses Apache Pulsar for event-driven communication:

- **Event Publishing**: Services publish domain events
- **Event Consumption**: Services subscribe to relevant events
- **Saga Pattern**: Choreography-based for distributed transactions
- **Event Sourcing**: Complete audit trail of all changes

## Testing

### Integration Tests
```bash
cd tests/integration
python -m pytest
```

### End-to-End Tests
```bash
cd tests/scripts
python test_final_integration.py
```

## 📚 Documentation

- [Architecture Overview](documentacion/arquitectura/OVERVIEW.md)
- [Microservices Design](documentacion/arquitectura/MICROSERVICES_DESIGN.md)
- [Saga Pattern Implementation](documentacion/patrones/SAGA_CHOREOGRAPHY.md)
- [Event Catalog](documentacion/eventos/EVENT_CATALOG.md)
- [Deployment Guide](documentacion/implementacion/DEPLOYMENT_GUIDE.md)
- [BFF GraphQL API](documentacion/bff/BFF_WEB_GRAPHQL.md)