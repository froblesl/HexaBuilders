# HexaBuilders - Enterprise Partner Management Platform

**HexaBuilders** is an enterprise-grade partner management platform built with modern architectural patterns and world-class design principles.

## Development Team

- **Francisco Robles** [@froblesl](https://github.com/froblesl)
- **Hernán Álvarez** [@hernanHawk](https://github.com/hernanHawk)
- **Nicolás Escobar** [@nicolasuniandes](https://github.com/nicolasuniandes)
- **Javier Barrera** [@j4vierb](https://github.com/j4vierb)

## Enterprise Architecture

HexaBuilders implements enterprise-level architectural patterns:

- **Domain-Driven Design (DDD)** - Domain-driven design approach
- **CQRS/CQS** - Command Query Responsibility Segregation
- **Event-Driven Architecture** - Event-based communication
- **Hexagonal Architecture** - Ports and Adapters pattern
- **Business Rules Engine** - Advanced business logic processing
- **Value Objects** - Immutable domain objects
- **Repository Pattern** - Data access abstraction
- **Unit of Work** - Transactional consistency

## Domain Modules

### 1. Partners Module
Complete 360-degree partner profile management:
- Partner onboarding and validation
- Support for Individual, Company, and Startup types
- Status management: Active, Inactive, Pending
- Advanced business rule validation
- Complete change history and event tracking

### 2. Campaigns Module  
Intelligent marketing campaign management:
- Campaign creation and configuration
- Partner assignment to campaigns
- Real-time performance tracking
- Conversion and engagement metrics
- Campaign ROI analysis

### 3. Commissions Module
Advanced commission calculation system:
- Automatic commission calculation
- Multiple commission schemes support
- Payment processing integration
- Complete transaction history
- Detailed financial reporting

### 4. Analytics Module
Business intelligence and 360-degree reporting:
- Real-time executive dashboard
- Partner performance metrics
- Predictive trend analysis
- Automated reporting
- Customizable KPIs

## Installation and Execution

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**

### Docker Execution (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/froblesl/HexaBuilders.git
cd HexaBuilders

# 2. Start infrastructure services
docker-compose up -d zookeeper pulsar-init bookie broker

# 3. Start main application
docker-compose up partner-management

# 4. Start notification service (optional)
docker-compose up notifications
```

### Local Development Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt -r pulsar-requirements.txt

# 2. Configure environment variables
export PYTHONPATH=./src
export PULSAR_BROKER_URL=pulsar://localhost:6650

# 3. Run the application
flask --app "partner_management.seedwork.presentacion.api:create_app" run --host 127.0.0.1 --port 5000
```

### Quick Start
```bash
# One-line command to run HexaBuilders
PYTHONPATH=./src flask --app "partner_management.seedwork.presentacion.api:create_app" run
```

## Testing and Quality Assurance

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific module tests
pytest tests/partner_management/
pytest tests/modulos/partners/
pytest tests/modulos/campaigns/
```

## API Endpoints

### Health & Status Monitoring
```http
GET /health              # General system status
GET /health/ready        # Readiness check
GET /health/live         # Liveness check
```

### Partners API (CQRS)

#### Commands (Write Operations)
```http
POST   /api/v1/partners-comando           # Create partner
PUT    /api/v1/partners-comando/{id}      # Update partner
DELETE /api/v1/partners-comando/{id}      # Deactivate partner
```

#### Queries (Read Operations)
```http
GET /api/v1/partners-query                # List partners
GET /api/v1/partners-query/{id}           # Get partner details
GET /api/v1/partners-query/{id}/profile360 # Complete 360 profile
```

### Campaigns API
```http
GET    /api/v1/campaigns                  # List campaigns
POST   /api/v1/campaigns                  # Create campaign
GET    /api/v1/campaigns/{id}             # Get campaign details
PUT    /api/v1/campaigns/{id}             # Update campaign
```

### Commissions API
```http
GET    /api/v1/commissions                # List commissions
POST   /api/v1/commissions/calculate      # Calculate commissions
GET    /api/v1/commissions/{partnerId}    # Partner commissions
```

## Project Structure

```
HexaBuilders/
├── src/
│   └── partner_management/           # Main service
│       ├── seedwork/                # Reusable base components
│       │   ├── dominio/            # Base entities and value objects
│       │   ├── aplicacion/         # Application patterns (CQRS)
│       │   ├── infraestructura/    # Adapters and infrastructure
│       │   └── presentacion/       # API and web interfaces
│       ├── modulos/                # Domain modules
│       │   ├── partners/           # Partner management
│       │   ├── campaigns/          # Campaign management
│       │   ├── commissions/        # Commission calculation
│       │   └── analytics/          # Analytics and reporting
│       └── api/                    # CQRS endpoints
├── tests/                          # Automated tests
├── .devcontainer/                  # Dev Container configuration
├── docker-compose.yml              # Service orchestration
├── requirements.txt                # Python dependencies
└── README.md                       # This documentation
```

## Technical Characteristics

### Domain-Driven Design
- **Aggregates** with complex business invariants
- **Entities** with unique identity and lifecycle
- **Value Objects** with immutable validations
- **Domain Services** for complex business logic
- **Domain Events** for internal communication

### CQRS/Event Sourcing
- **Commands** for write operations
- **Queries** optimized for read operations
- **Event Store** for event persistence
- **Projections** for materialized views
- **Saga Pattern** for distributed transactions

### Implemented Patterns
- **Repository Pattern** - Data persistence abstraction
- **Unit of Work** - Atomic transactions
- **Factory Pattern** - Complex object creation
- **Strategy Pattern** - Interchangeable algorithms
- **Observer Pattern** - Event handling
- **Command Pattern** - Operation encapsulation

## Advanced Configuration

### Environment Variables
```bash
# Application
PYTHONPATH=./src
FLASK_ENV=development
FLASK_DEBUG=true

# Database
DATABASE_URL=sqlite:///hexabuilders.db
DATABASE_POOL_SIZE=10

# Message Broker
PULSAR_BROKER_URL=pulsar://localhost:6650
PULSAR_TOPIC_PREFIX=hexabuilders

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Compose Services
- **Zookeeper** - Distributed coordination
- **Apache Pulsar** - Message broker
- **HexaBuilders API** - Main application  
- **Notifications** - Notification service

## Monitoring and Observability

HexaBuilders includes comprehensive observability:

- **Application Metrics** - Performance and usage tracking
- **Structured Logging** - Structured log output
- **Correlation IDs** - Request traceability
- **Health Checks** - Kubernetes readiness
- **Business Metrics** - Business KPI tracking

## Contribution Guidelines

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-functionality`)
3. Commit changes (`git commit -m 'Add new functionality'`)
4. Push to branch (`git push origin feature/new-functionality`)
5. Create Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

## Acknowledgments

Developed following best practices from:
- **Domain-Driven Design** - Eric Evans
- **Clean Architecture** - Robert C. Martin  
- **Enterprise Integration Patterns** - Gregor Hohpe
- **Microservices Patterns** - Chris Richardson

---

**Repository**: https://github.com/froblesl/HexaBuilders  
**Contact**: francisco.robles@hexabuilders.com

---

*HexaBuilders - Building Enterprise Solutions with Hexagonal Architecture*