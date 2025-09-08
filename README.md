# HexaBuilders - Enterprise Partner Management Platform

**HexaBuilders** es una plataforma empresarial de gestión de partners construida con arquitecturas modernas y patrones de diseño de clase mundial.

## 👥 Equipo de Desarrollo

- **Francisco Robles** [@froblesl](https://github.com/froblesl)
- **Hernán Álvarez** [@hernanHawk](https://github.com/hernanHawk)
- **Nicolás Escobar** [@nicolasuniandes](https://github.com/nicolasuniandes)
- **Javier Barrera** [@j4vierb](https://github.com/j4vierb)

## 🏗️ Arquitectura Empresarial

HexaBuilders implementa patrones arquitectónicos de nivel empresarial:

- ⚡ **Domain-Driven Design (DDD)** - Diseño dirigido por el dominio
- 🔄 **CQRS/CQS** - Separación de comandos y consultas
- 📡 **Event-Driven Architecture** - Arquitectura dirigida por eventos
- 🛡️ **Hexagonal Architecture** - Puertos y adaptadores
- 🔧 **Business Rules Engine** - Motor de reglas de negocio
- 💎 **Value Objects** - Objetos de valor inmutables
- 🏛️ **Repository Pattern** - Patrón repositorio
- ⚖️ **Unit of Work** - Unidad de trabajo transaccional

## 🌟 Módulos de Dominio

### 1. 🤝 Partners Module
Gestión completa del perfil 360 de partners empresariales:
- Onboarding y validación de partners
- Gestión de tipos: Individual, Empresa, Startup
- Estados: Activo, Inactivo, Pendiente
- Validaciones de negocio avanzadas
- Historial de cambios y eventos

### 2. 📊 Campaigns Module  
Gestión inteligente de campañas de marketing:
- Creación y configuración de campañas
- Asignación de partners a campañas
- Seguimiento de performance en tiempo real
- Métricas de conversión y engagement
- Análisis de ROI por campaña

### 3. 💰 Commissions Module
Sistema avanzado de cálculo de comisiones:
- Cálculo automático de comisiones
- Múltiples esquemas de comisión
- Procesamiento de pagos
- Historial completo de transacciones
- Reportes financieros detallados

### 4. 📈 Analytics Module
Inteligencia de negocio y reportes 360:
- Dashboard ejecutivo en tiempo real
- Métricas de rendimiento de partners
- Análisis predictivo de tendencias  
- Reportes automatizados
- KPIs personalizables

## 🚀 Instalación y Ejecución

### Prerequisitos
- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**

### 🐳 Ejecución con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/froblesl/HexaBuilders.git
cd HexaBuilders

# 2. Iniciar servicios de infraestructura
docker-compose up -d zookeeper pulsar-init bookie broker

# 3. Iniciar la aplicación principal
docker-compose up partner-management

# 4. Iniciar servicio de notificaciones (opcional)
docker-compose up notifications
```

### 🛠️ Ejecución en Desarrollo Local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt -r pulsar-requirements.txt

# 2. Configurar variables de entorno
export PYTHONPATH=./src
export PULSAR_BROKER_URL=pulsar://localhost:6650

# 3. Ejecutar la aplicación
flask --app "partner_management.seedwork.presentacion.api:create_app" run --host 127.0.0.1 --port 5000
```

### ⚡ Inicio Rápido
```bash
# Una línea para ejecutar HexaBuilders
PYTHONPATH=./src flask --app "partner_management.seedwork.presentacion.api:create_app" run
```

## 🧪 Testing y Calidad

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src --cov-report=html

# Tests de módulos específicos
pytest tests/partner_management/
pytest tests/modulos/partners/
pytest tests/modulos/campaigns/
```

## 📡 API Endpoints

### 🔍 Health & Status
```http
GET /health              # Estado general del sistema
GET /health/ready        # Verificación de preparación
GET /health/live         # Verificación de vida
```

### 👥 Partners API (CQRS)

#### Commands (Escritura)
```http
POST   /api/v1/partners-comando           # Crear partner
PUT    /api/v1/partners-comando/{id}      # Actualizar partner
DELETE /api/v1/partners-comando/{id}      # Desactivar partner
```

#### Queries (Lectura)
```http
GET /api/v1/partners-query                # Listar partners
GET /api/v1/partners-query/{id}           # Obtener partner
GET /api/v1/partners-query/{id}/profile360 # Perfil completo 360
```

### 📊 Campaigns API
```http
GET    /api/v1/campaigns                  # Listar campañas
POST   /api/v1/campaigns                  # Crear campaña
GET    /api/v1/campaigns/{id}             # Obtener campaña
PUT    /api/v1/campaigns/{id}             # Actualizar campaña
```

### 💰 Commissions API
```http
GET    /api/v1/commissions                # Listar comisiones
POST   /api/v1/commissions/calculate      # Calcular comisiones
GET    /api/v1/commissions/{partnerId}    # Comisiones por partner
```

## 📁 Estructura del Proyecto

```
HexaBuilders/
├── 📂 src/
│   └── 📂 partner_management/           # Servicio principal
│       ├── 📂 seedwork/                # Componentes base reutilizables
│       │   ├── 📂 dominio/            # Entidades y objetos valor base
│       │   ├── 📂 aplicacion/         # Patrones de aplicación (CQRS)
│       │   ├── 📂 infraestructura/    # Adaptadores e infraestructura
│       │   └── 📂 presentacion/       # API y interfaces web
│       ├── 📂 modulos/                # Módulos de dominio
│       │   ├── 📂 partners/           # Gestión de partners
│       │   ├── 📂 campaigns/          # Gestión de campañas
│       │   ├── 📂 commissions/        # Cálculo de comisiones
│       │   └── 📂 analytics/          # Analytics y reportes
│       └── 📂 api/                    # Endpoints CQRS
├── 📂 tests/                          # Tests automatizados
├── 📂 .devcontainer/                  # Configuración Dev Container
├── 🐳 docker-compose.yml              # Orquestación de servicios
├── 📋 requirements.txt                # Dependencias Python
└── 📖 README.md                       # Esta documentación
```

## 🎯 Características Técnicas

### 💎 Domain-Driven Design
- **Agregados** complejos con invariantes de negocio
- **Entidades** con identidad única y ciclo de vida
- **Objetos de Valor** inmutables con validaciones
- **Servicios de Dominio** para lógica compleja
- **Eventos de Dominio** para comunicación interna

### ⚡ CQRS/Event Sourcing
- **Comandos** para operaciones de escritura
- **Queries** optimizadas para lectura
- **Event Store** para persistencia de eventos
- **Proyecciones** para vistas materializadas
- **Saga Pattern** para transacciones distribuidas

### 🛡️ Patterns Implementados
- **Repository Pattern** - Abstracción de persistencia
- **Unit of Work** - Transacciones atómicas
- **Factory Pattern** - Creación de objetos complejos
- **Strategy Pattern** - Algoritmos intercambiables
- **Observer Pattern** - Manejo de eventos
- **Command Pattern** - Encapsulación de operaciones

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Aplicación
PYTHONPATH=./src
FLASK_ENV=development
FLASK_DEBUG=true

# Base de datos
DATABASE_URL=sqlite:///hexabuilders.db
DATABASE_POOL_SIZE=10

# Message Broker
PULSAR_BROKER_URL=pulsar://localhost:6650
PULSAR_TOPIC_PREFIX=hexabuilders

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Compose Servicios
- **🐘 Zookeeper** - Coordinación distribuida
- **📡 Apache Pulsar** - Message Broker
- **📊 HexaBuilders API** - Aplicación principal  
- **🔔 Notifications** - Servicio de notificaciones

## 📊 Métricas y Monitoreo

HexaBuilders incluye observabilidad completa:

- **📈 Métricas de aplicación** - Performance y uso
- **📝 Structured Logging** - Logs estructurados
- **🔍 Correlation IDs** - Trazabilidad de requests
- **⚡ Health Checks** - Kubernetes ready
- **📊 Business Metrics** - KPIs de negocio

## 🤝 Contribución

1. Fork el repositorio
2. Crear branch feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📋 Roadmap

### ✅ Completado
- [x] Arquitectura DDD/CQRS completa
- [x] 4 módulos de dominio funcionales
- [x] API REST con Flask
- [x] Patrones empresariales implementados
- [x] Tests unitarios y de integración

### 🚀 Próximas Versiones
- [ ] Dashboard web interactivo
- [ ] APIs GraphQL
- [ ] Microservicios independientes
- [ ] Machine Learning para analytics
- [ ] Integración con sistemas ERP
- [ ] Mobile app para partners

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🏆 Reconocimientos

Desarrollado siguiendo las mejores prácticas de:
- **Domain-Driven Design** - Eric Evans
- **Clean Architecture** - Robert C. Martin  
- **Enterprise Integration Patterns** - Gregor Hohpe
- **Microservices Patterns** - Chris Richardson

---

⭐ **¡Dale una estrella al proyecto si te gustó!** ⭐

🔗 **Repositorio**: https://github.com/froblesl/HexaBuilders  
📧 **Contacto**: francisco.robles@hexabuilders.com

---

*HexaBuilders - Building Enterprise Solutions with Hexagonal Architecture* 🏗️