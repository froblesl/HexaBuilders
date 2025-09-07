# Alpes Partners - Partner Management Profile 360

Miembros del equipo:
- Francisco Robles @froblesl
- Hernán Álvarez @hernanHawk
- Nicolás Escobar @nicolasuniandes
- Javier barrera @j4vierb

Microservicio de gestión de partners implementando arquitectura DDD, CQRS y basada en eventos.

## Características

- **Domain-Driven Design (DDD)** completo con agregaciones, entidades, objetos valor
- **CQRS/CQS** para separación de comandos y consultas
- **Arquitectura basada en eventos** con Apache Pulsar
- **Arquitectura hexagonal** (puertos y adaptadores)
- **Unidad de Trabajo** para consistencia transaccional
- **Schema Registry** con Avro para versionado de eventos

## Módulos de Dominio

### 1. Partners
Gestión completa del perfil 360 de partners, incluyendo onboarding, validación, y mantenimiento de perfiles.

### 2. Campaigns
Gestión de campañas de marketing, asignación de partners y seguimiento de performance.

### 3. Commissions
Cálculo, procesamiento y gestión de comisiones con historial completo.

### 4. Analytics
Métricas, reportes y analytics 360 para partners y campañas.

## Instalación y Ejecución

### Prerequisitos
- Docker y Docker Compose
- Python 3.11+

### Ejecución con Docker
```bash
# Iniciar servicios de Pulsar
docker-compose up -d zookeeper pulsar-init bookie broker

# Iniciar el microservicio
docker-compose up partner-management

# Iniciar servicio de notificaciones
docker-compose up notifications
```

### Ejecución en desarrollo
```bash
# Instalar dependencias
pip install -r requirements.txt -r pulsar-requirements.txt

# Configurar variables de entorno
export PULSAR_BROKER_URL=pulsar://localhost:6650
export DATABASE_URL=

# Ejecutar el servicio
python -m partner_management.api.partners
```

## Testing
```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html
```

## Arquitectura

El proyecto sigue los principios de DDD con una clara separación de responsabilidades:

- **Seedwork**: Componentes base reutilizables
- **Módulos de Dominio**: Lógica de negocio encapsulada
- **Eventos de Dominio**: Comunicación interna entre módulos
- **Eventos de Integración**: Comunicación con servicios externos
- **Apache Pulsar**: Broker de eventos escalable

## API Endpoints

### Partners
- `POST /partners` - Crear partner
- `GET /partners/{id}` - Obtener partner
- `PUT /partners/{id}` - Actualizar partner
- `GET /partners/{id}/profile360` - Obtener perfil 360