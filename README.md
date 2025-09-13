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

**⚠️ Importante**: Temporalmente renombrar el archivo override para evitar conflictos:
```bash
mv docker-compose.override.yml docker-compose.override.yml.bak
```

**Opción 1: Levantar todos los servicios** 
```bash
# 1. Clone the repository
git clone https://github.com/froblesl/HexaBuilders.git
cd HexaBuilders

# 2. Levantar infraestructura completa (PostgreSQL, Pulsar, Elasticsearch)
docker-compose -f docker-compose.simple.yml --profile database --profile pulsar --profile elasticsearch up -d

# 3. Esperar a que los servicios estén listos (60 segundos)
sleep 60

# 4. Levantar todos los microservicios
docker-compose -f docker-compose.simple.yml --profile services up -d

# 5. Verificar estado
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Opción 2: Solo servicios principales (sin Elasticsearch/Recruitment)**
```bash
# 1. Levantar infraestructura base
docker-compose --profile database --profile pulsar up -d

# 2. Construir imágenes específicas
docker build -t hexabuilders-partner-management -f src/partner_management/Dockerfile .
docker build -t hexabuilders-onboarding -f src/onboarding/Dockerfile .
docker build -t hexabuilders-campaign-management -f src/campaign_management/Dockerfile .
docker build -t hexabuilders-notifications -f notifications.Dockerfile .

# 3. Esperar que infraestructura esté lista
sleep 30

# 4. Levantar servicios construidos
docker run -d --name partner-management --network hexabuilders_pulsar \
  -e DATABASE_URL="postgresql://hexabuilders_user:hexabuilders_password@postgres:5432/hexabuilders" \
  -e PULSAR_BROKER_URL="pulsar://broker:6650" \
  -p 5000:5000 hexabuilders-partner-management

# Repetir para otros servicios según necesites
```

### One-Command Startup (Todos los Servicios)

```bash
# Renombrar override y levantar todo de una vez
mv docker-compose.override.yml docker-compose.override.yml.bak && \
docker-compose -f docker-compose.simple.yml --profile database --profile pulsar --profile elasticsearch --profile services up --build -d

# Esperar y probar
sleep 90 && curl http://localhost:5000/health
```

### Servicios Disponibles Una Vez Levantados

```bash
# Partner Management API
curl http://localhost:5000/health
curl http://localhost:5000/api/v1/partners-query

# Onboarding API  
curl http://localhost:5001/health

# Recruitment API (requiere Elasticsearch)
curl http://localhost:5002/health

# Campaign Management API
curl http://localhost:5003/health  

# Notifications Service
curl http://localhost:5004/health
```

### Service Status Verification

```bash
# Check all running containers
docker-compose ps

# View application logs
docker-compose logs -f partner-management

# View PostgreSQL logs
docker-compose logs postgres

# View Pulsar broker logs
docker-compose logs broker
```

### Local Development Execution

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt -r pulsar-requirements.txt

# 3. Start infrastructure only (Docker)
docker-compose --profile database --profile pulsar up -d

# 4. Configure environment variables
export PYTHONPATH=./src
export DATABASE_URL="postgresql://hexabuilders_user:hexabuilders_password@localhost:5433/hexabuilders"
export PULSAR_BROKER_URL="pulsar://localhost:6650"

# 5. Run the application
flask --app "partner_management.seedwork.presentacion.api:create_app" run --host 127.0.0.1 --port 5000
```

### Quick Start
```bash
# One-line command to run HexaBuilders (after infrastructure is up)
PYTHONPATH=./src DATABASE_URL="postgresql://hexabuilders_user:hexabuilders_password@localhost:5433/hexabuilders" PULSAR_BROKER_URL="pulsar://localhost:6650" flask --app "partner_management.seedwork.presentacion.api:create_app" run
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

# PostgreSQL Database
DATABASE_URL=postgresql://hexabuilders_user:hexabuilders_password@localhost:5432/hexabuilders
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# Message Broker
PULSAR_BROKER_URL=pulsar://localhost:6650
PULSAR_TOPIC_PREFIX=hexabuilders

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use (PostgreSQL)
```bash
# Error: "bind: address already in use" on port 5432
# Solution: The compose file uses port 5433 to avoid conflicts
# Check if PostgreSQL is running: lsof -i :5432
```

#### 2. pulsar-init Container Not Running
```bash
# This is NORMAL - pulsar-init is a one-time setup container
# Check if it completed successfully:
docker-compose logs pulsar-init

# Should show: "Cluster metadata for 'cluster-a' setup correctly"
```

#### 3. Application Won't Start
```bash
# Check if all dependencies are running:
docker-compose ps

# Ensure these are healthy/running:
# - hexabuilders-postgres (healthy)
# - zookeeper (healthy)
# - broker (running)
# - bookie (running)

# Restart sequence if needed:
docker-compose --profile database --profile pulsar --profile partner-management down
docker-compose --profile database --profile pulsar up -d
sleep 30
docker-compose --profile partner-management up -d
```

#### 4. Connection Refused Errors
```bash
# Wait for services to fully start:
sleep 30

# Check service health:
curl http://localhost:5000/health
curl http://localhost:8080/admin/v2/brokers/health

# Check PostgreSQL connection:
docker exec -it hexabuilders-postgres pg_isready -U hexabuilders_user -d hexabuilders
```

### Cleanup and Restart

```bash
# Stop all services
docker-compose --profile database --profile pulsar --profile partner-management down

# Remove volumes (WARNING: This deletes all data)
docker-compose --profile database --profile pulsar --profile partner-management down -v

# Restart fresh
docker-compose --profile database --profile pulsar up -d
sleep 30
docker-compose --profile partner-management up -d

# Clean rebuild (if needed)
docker-compose --profile database --profile pulsar --profile partner-management down -v
docker build -t hexabuilders-partner-management -f partner-management.Dockerfile .
docker-compose --profile database --profile pulsar --profile partner-management up --build -d
```

### Service Monitoring

```bash
# Real-time logs
docker-compose logs -f partner-management
docker-compose logs -f broker
docker-compose logs -f postgres

# Check resource usage
docker stats

# Access PostgreSQL directly
docker exec -it hexabuilders-postgres psql -U hexabuilders_user -d hexabuilders

# Test Pulsar broker
curl http://localhost:8080/admin/v2/brokers/ready
```

### Docker Compose Services
- **PostgreSQL** - Enterprise-grade relational database (Port 5433)
- **Zookeeper** - Distributed coordination (Internal)
- **Apache Pulsar Broker** - Message broker (Ports 6650, 8080)
- **Apache BookKeeper** - Persistent message storage (Internal)  
- **pulsar-init** - One-time initialization container (Exits after setup)
- **HexaBuilders API** - Main application (Port 5000)
- **Notifications** - Notification service (Internal)

### Important Notes

- **pulsar-init** is a one-time initialization container that sets up Pulsar cluster metadata and then exits. This is normal behavior.
- PostgreSQL runs on port **5433** to avoid conflicts with local PostgreSQL installations.
- All services use Docker networks for internal communication.

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
