# Guía de Configuración de Desarrollo - HexaBuilders

## 🛠️ Pre-requisitos

### **Herramientas Requeridas**
- **Python 3.11+**
- **Docker 20.10+** y **Docker Compose 2.0+**
- **Git**
- **IDE**: VS Code, PyCharm, o similar
- **Postman/Insomnia** para testing de APIs

### **Configuración del Sistema**
```bash
# Verificar versiones
python --version    # >= 3.11
docker --version    # >= 20.10
docker-compose --version  # >= 2.0
```

---

## 🏗️ Configuración Inicial

### **1. Clonar y Configurar Repositorio**
```bash
# Clonar repositorio
git clone <repository-url>
cd HexaBuilders

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r pulsar-requirements.txt
pip install -r dev-requirements.txt
```

### **2. Variables de Entorno**
```bash
# Crear archivo .env.development
cat > .env.development << EOF
# Database Configuration
DATABASE_URL=postgresql://hexauser:hexapass123@localhost:5432/hexabuilders_dev
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_hexabuilders

# Pulsar Configuration  
PULSAR_SERVICE_URL=pulsar://localhost:6650
PULSAR_WEB_SERVICE_URL=http://localhost:8080

# Service Configuration
FLASK_ENV=development
LOG_LEVEL=DEBUG
JWT_SECRET_KEY=development-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# ElasticSearch (for Recruitment service)
ELASTICSEARCH_URL=http://localhost:9200

# Service Ports
PARTNER_MANAGEMENT_PORT=5000
ONBOARDING_PORT=5001
RECRUITMENT_PORT=5002
CAMPAIGN_MANAGEMENT_PORT=5003
NOTIFICATIONS_PORT=5004
EOF

# Cargar variables
source .env.development
```

### **3. Infraestructura con Docker**
```bash
# Iniciar solo servicios de infraestructura
docker-compose -f docker-compose.dev.yml up -d postgres zookeeper bookie broker elasticsearch

# Verificar que servicios estén corriendo
docker-compose ps
```

---

## 🐘 Configuración de Base de Datos

### **Configuración PostgreSQL**
```bash
# Conectar a PostgreSQL
docker exec -it hexabuilders-postgres psql -U hexauser -d hexabuilders_dev

# Crear bases de datos para cada servicio
CREATE DATABASE partner_management_dev;
CREATE DATABASE onboarding_dev;
CREATE DATABASE recruitment_dev;
CREATE DATABASE campaign_management_dev;
CREATE DATABASE notifications_dev;

# Base de datos para testing
CREATE DATABASE test_hexabuilders;
CREATE USER test_user WITH ENCRYPTED PASSWORD 'test_pass';
GRANT ALL PRIVILEGES ON DATABASE test_hexabuilders TO test_user;
```

### **Migraciones de Base de Datos**
```bash
# Ejecutar migraciones para cada servicio
cd src/partner_management
python -m seedwork.infraestructura.database.migrations

cd ../onboarding
python -m infraestructura.database.migrations

cd ../recruitment
python -m infraestructura.database.migrations

cd ../campaign_management
python -m infraestructura.database.migrations
```

---

## 🔧 Configuración por Servicio

### **Partner Management Service**
```bash
# Navegar al servicio
cd src/partner_management

# Variables específicas
export SERVICE_NAME="partner-management"
export DATABASE_URL="postgresql://hexauser:hexapass123@localhost:5432/partner_management_dev"

# Ejecutar en modo desarrollo
python -m api.partners

# En otra terminal, verificar
curl http://localhost:5000/health
```

### **Onboarding Service**
```bash
cd src/onboarding

export SERVICE_NAME="onboarding"
export DATABASE_URL="postgresql://hexauser:hexapass123@localhost:5432/onboarding_dev"
export PORT=5001

python -m api.contracts

# Verificar
curl http://localhost:5001/health
```

### **Recruitment Service**
```bash
cd src/recruitment

export SERVICE_NAME="recruitment"
export DATABASE_URL="postgresql://hexauser:hexapass123@localhost:5432/recruitment_dev"
export ELASTICSEARCH_URL="http://localhost:9200"
export PORT=5002

# Configurar índices de ElasticSearch
python -m infraestructura.elasticsearch.setup

python -m api.candidates

# Verificar
curl http://localhost:5002/health
```

### **Campaign Management Service**
```bash
cd src/campaign_management

export SERVICE_NAME="campaign-management"
export DATABASE_URL="postgresql://hexauser:hexapass123@localhost:5432/campaign_management_dev"
export PORT=5003

python -m api.campaigns

# Verificar
curl http://localhost:5003/health
```

---

## 🧪 Configuración de Testing

### **Estructura de Tests**
```
tests/
├── unit/                          # Tests unitarios
│   ├── partner_management/
│   ├── onboarding/
│   ├── recruitment/
│   └── campaign_management/
├── integration/                   # Tests de integración
│   ├── api/
│   ├── database/
│   └── events/
├── e2e/                          # Tests end-to-end
│   └── scenarios/
├── fixtures/                     # Datos de prueba
└── conftest.py                   # Configuración pytest
```

### **Configuración pytest**
```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=html:htmlcov",
    "--cov-report=term-missing",
    "--cov-fail-under=80"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "e2e: End-to-end tests",
    "slow: Slow running tests"
]
```

### **Fixtures Globales**
```python
# tests/conftest.py
import pytest
import asyncio
from unittest.mock import Mock
from src.partner_management.seedwork.infraestructura.uow import SqlAlchemyUoW
from src.partner_management.seedwork.infraestructura.pulsar import PulsarEventBus

@pytest.fixture
def mock_uow():
    return Mock(spec=SqlAlchemyUoW)

@pytest.fixture
def mock_event_bus():
    return Mock(spec=PulsarEventBus)

@pytest.fixture
def sample_partner_data():
    return {
        "nombre": "Test Partner",
        "email": "test@partner.com",
        "telefono": "+1234567890",
        "tipo": "INDIVIDUAL"
    }

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### **Comandos de Testing**
```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v -m "not slow"

# Tests completos con cobertura
pytest --cov=src --cov-report=html

# Tests específicos de un servicio
pytest tests/unit/partner_management/ -v

# Tests con markers
pytest -m "unit and not slow" -v

# Tests con debugging
pytest tests/unit/partner_management/test_entities.py::TestPartner::test_create_partner -v -s
```

---

## 🔍 Herramientas de Desarrollo

### **Pre-commit Hooks**
```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Instalar hooks
pre-commit install
```

### **Linting y Formatting**
```bash
# Formatear código
black src/ tests/

# Organizar imports
isort src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Todo en uno
pre-commit run --all-files
```

### **VS Code Configuration**
```json
# .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".coverage": true,
        "htmlcov/": true
    }
}
```

---

## 🐛 Debugging

### **Debugging con VS Code**
```json
# .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Partner Management API",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/partner_management/api/partners.py",
            "env": {
                "FLASK_ENV": "development",
                "DATABASE_URL": "postgresql://hexauser:hexapass123@localhost:5432/partner_management_dev"
            },
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Pytest Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v", "-s"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### **Logging Configuration**
```python
# src/partner_management/seedwork/infraestructura/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(service_name: str, level: str = "INFO"):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Add service name to all logs
    logging.getLogger().addFilter(
        lambda record: setattr(record, 'service', service_name) or True
    )
    
    return logger
```

---

## 📊 Monitoreo en Desarrollo

### **Health Checks**
```bash
# Script para verificar todos los servicios
#!/bin/bash
# dev-health-check.sh

services=(
    "Partner Management:5000"
    "Onboarding:5001" 
    "Recruitment:5002"
    "Campaign Management:5003"
    "Notifications:5004"
)

echo "🏥 Health Check - HexaBuilders Services"
echo "======================================"

for service in "${services[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    echo -n "Checking $name ($port)... "
    
    if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ HEALTHY"
    else
        echo "❌ DOWN"
    fi
done

echo ""
echo "🔍 Infrastructure Status:"
echo "========================"

# PostgreSQL
echo -n "PostgreSQL... "
if docker exec hexabuilders-postgres pg_isready > /dev/null 2>&1; then
    echo "✅ READY"
else
    echo "❌ DOWN"
fi

# Pulsar
echo -n "Pulsar... "
if curl -sf "http://localhost:8080/admin/v2/clusters" > /dev/null 2>&1; then
    echo "✅ READY"
else
    echo "❌ DOWN"
fi

# ElasticSearch
echo -n "ElasticSearch... "
if curl -sf "http://localhost:9200/_cluster/health" > /dev/null 2>&1; then
    echo "✅ READY"
else
    echo "❌ DOWN"
fi
```

### **Makefile para Comandos Comunes**
```makefile
# Makefile
.PHONY: install test lint format dev-setup dev-start dev-stop health-check

install:
	pip install -r requirements.txt
	pip install -r pulsar-requirements.txt
	pip install -r dev-requirements.txt

test:
	pytest tests/ -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

dev-setup:
	docker-compose -f docker-compose.dev.yml up -d postgres zookeeper bookie broker elasticsearch
	sleep 10
	@echo "Infrastructure ready! Run 'make dev-start' to start services"

dev-start:
	@echo "Starting all services..."
	@bash scripts/start-all-services.sh

dev-stop:
	@echo "Stopping all services..."
	@bash scripts/stop-all-services.sh
	docker-compose -f docker-compose.dev.yml down

health-check:
	@bash scripts/dev-health-check.sh

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -f .coverage
```

---

Esta guía proporciona todo lo necesario para configurar un entorno de desarrollo completo y productivo para HexaBuilders, con herramientas modernas de desarrollo, testing y debugging.