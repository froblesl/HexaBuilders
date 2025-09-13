# Guía de Migración - HexaBuilders

## 🔄 Migración desde Partner Management Monolítico

### **Contexto de la Migración**

Esta guía detalla cómo migrar el sistema actual de Partner Management (monolítico) hacia la arquitectura de microservicios con 4 servicios independientes:

1. **Partner Management** (Existente - Refactorizado)
2. **Onboarding** (Nuevo)
3. **Recruitment** (Nuevo)  
4. **Campaign Management** (Nuevo)

---

## 📋 Plan de Migración

### **Fase 1: Preparación y Análisis (Semanas 1-2)**

#### **1.1 Análisis de Dependencias**
```bash
# Auditar código existente
cd src/partner_management

# Identificar dependencias entre módulos
grep -r "from.*campaigns" modulos/
grep -r "from.*commissions" modulos/
grep -r "import.*analytics" modulos/

# Analizar base de datos
psql -d hexabuilders -c "\dt" | grep -E "(campaign|commission|analytics)"
```

#### **1.2 Mapeo de Funcionalidades**
| Funcionalidad Actual | Servicio Destino | Complejidad | Estrategia |
|---------------------|------------------|-------------|------------|
| Partner CRUD | Partner Management | ✅ Baja | Mantener |
| Partner Validation | Partner Management | ✅ Baja | Mantener |
| Profile 360 | Partner Management | 🟡 Media | Refactorizar |
| Campaign CRUD | Campaign Management | 🔴 Alta | Extraer |
| Campaign Analytics | Campaign Management | 🔴 Alta | Extraer |
| Commission Calculation | Partner Management | 🟡 Media | Mantener |
| Contract Management | Onboarding | 🔴 Alta | Extraer |

#### **1.3 Preparación del Entorno**
```bash
# Crear ramas para migración
git checkout -b migration/phase1-preparation
git checkout -b migration/phase2-extraction
git checkout -b migration/phase3-integration

# Backup de base de datos
pg_dump hexabuilders > backup_pre_migration.sql

# Configurar entorno de pruebas
cp .env .env.migration.backup
```

---

### **Fase 2: Extracción de Servicios (Semanas 3-6)**

#### **2.1 Extracción del Campaign Management**

##### **Paso 1: Crear Estructura del Nuevo Servicio**
```bash
# Crear estructura
mkdir -p src/campaign_management/{modulos,seedwork,api}
mkdir -p src/campaign_management/modulos/{campaigns,performance,budget}
mkdir -p src/campaign_management/seedwork/{dominio,aplicacion,infraestructura,presentacion}

# Copiar seedwork base
cp -r src/partner_management/seedwork/* src/campaign_management/seedwork/
```

##### **Paso 2: Migrar Entidades de Campaign**
```python
# src/campaign_management/modulos/campaigns/dominio/entidades.py

# ANTES (en partner_management)
from partner_management.modulos.campaigns.dominio.entidades import Campaign

# DESPUÉS (en campaign_management)
from campaign_management.modulos.campaigns.dominio.entidades import Campaign

# Actualizar imports en toda la aplicación
find src/partner_management -name "*.py" -exec sed -i 's/from.*campaigns/from campaign_management.modulos.campaigns/g' {} \;
```

##### **Paso 3: Migrar Base de Datos**
```sql
-- Migración de tablas de Campaign
-- migration_001_extract_campaigns.sql

-- 1. Crear nueva base de datos para Campaign Management
CREATE DATABASE campaign_management;

-- 2. Conectar a nueva DB y crear tablas
\c campaign_management;

-- 3. Migrar estructura
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    partner_id UUID NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    presupuesto DECIMAL(10,2),
    estado VARCHAR(50),
    fecha_inicio DATE,
    fecha_fin DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE campaign_performance (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    metricas JSONB,
    fecha DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Migrar datos
\c hexabuilders;
\copy (SELECT * FROM campaigns) TO '/tmp/campaigns_data.csv' CSV HEADER;
\copy (SELECT * FROM campaign_performance) TO '/tmp/performance_data.csv' CSV HEADER;

\c campaign_management;
\copy campaigns FROM '/tmp/campaigns_data.csv' CSV HEADER;
\copy campaign_performance FROM '/tmp/performance_data.csv' CSV HEADER;
```

##### **Paso 4: Configurar APIs y Eventos**
```python
# src/campaign_management/api/campaigns.py
from flask import Flask
from campaign_management.seedwork.presentacion.api import crear_app

app = crear_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
```

#### **2.2 Extracción del Onboarding Service**

##### **Paso 1: Identificar Lógica de Contratos**
```bash
# Buscar funcionalidades relacionadas con contratos
grep -r "contract" src/partner_management/modulos/partners/
grep -r "onboard" src/partner_management/modulos/partners/
grep -r "agreement" src/partner_management/modulos/partners/
```

##### **Paso 2: Crear Service de Onboarding**
```python
# src/onboarding/modulos/contracts/dominio/entidades.py
from dataclasses import dataclass
from datetime import datetime
from onboarding.seedwork.dominio.entidades import AggregateRoot

@dataclass
class Contract(AggregateRoot):
    partner_id: str
    tipo_contrato: str
    estado: str = "DRAFT"
    terminos: dict = None
    fecha_creacion: datetime = None
    
    def firmar_contrato(self):
        if self.estado != "PENDING_SIGNATURE":
            raise ValueError("Contract must be in PENDING_SIGNATURE state")
        self.estado = "SIGNED"
        self.publicar_evento(ContractSigned(self.id, self.partner_id))
```

##### **Paso 3: Event Sourcing para Contratos**
```python
# src/onboarding/seedwork/infraestructura/event_store.py
class ContractEventStore:
    def __init__(self, db_session):
        self.session = db_session
    
    def save_events(self, aggregate_id: str, events: list, expected_version: int):
        for i, event in enumerate(events):
            event_record = EventRecord(
                aggregate_id=aggregate_id,
                version=expected_version + i + 1,
                event_type=event.__class__.__name__,
                event_data=event.to_dict(),
                timestamp=datetime.utcnow()
            )
            self.session.add(event_record)
        self.session.commit()
```

#### **2.3 Extracción del Recruitment Service**

##### **Paso 1: Configurar ElasticSearch**
```python
# src/recruitment/infraestructura/elasticsearch/setup.py
from elasticsearch import Elasticsearch

def setup_indices():
    es = Elasticsearch('http://localhost:9200')
    
    # Índice para candidatos
    candidate_mapping = {
        "mappings": {
            "properties": {
                "name": {"type": "text", "analyzer": "standard"},
                "skills": {"type": "keyword"},
                "experience_years": {"type": "integer"},
                "location": {"type": "keyword"},
                "availability": {"type": "keyword"},
                "profile_summary": {"type": "text"}
            }
        }
    }
    
    es.indices.create(index="candidates", body=candidate_mapping, ignore=400)
    
    # Índice para trabajos
    job_mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "required_skills": {"type": "keyword"},
                "experience_required": {"type": "integer"},
                "location": {"type": "keyword"},
                "status": {"type": "keyword"}
            }
        }
    }
    
    es.indices.create(index="jobs", body=job_mapping, ignore=400)
```

---

### **Fase 3: Configuración de Comunicación (Semanas 7-8)**

#### **3.1 Event-Driven Integration**

##### **Partner Management → Onboarding**
```python
# src/partner_management/modulos/partners/dominio/eventos.py
@dataclass
class PartnerRegistrationCompleted(IntegrationEvent):
    partner_id: str
    partner_data: dict
    
    def to_dict(self):
        return {
            "partner_id": self.partner_id,
            "partner_data": self.partner_data,
            "timestamp": self.timestamp.isoformat()
        }
```

```python
# src/onboarding/aplicacion/handlers/partner_events.py
class PartnerRegistrationHandler:
    def __init__(self, contract_repository, uow):
        self.repository = contract_repository
        self.uow = uow
    
    async def handle(self, event: PartnerRegistrationCompleted):
        with self.uow:
            # Crear borrador de contrato automáticamente
            contract = Contract(
                partner_id=event.partner_id,
                tipo_contrato="STANDARD",
                estado="DRAFT"
            )
            await self.repository.save(contract)
            self.uow.commit()
```

##### **Onboarding → Campaign Management**
```python
# src/onboarding/modulos/contracts/dominio/eventos.py
@dataclass  
class ContractActivated(IntegrationEvent):
    partner_id: str
    contract_id: str
    contract_type: str
```

```python
# src/campaign_management/aplicacion/handlers/contract_events.py
class ContractActivatedHandler:
    async def handle(self, event: ContractActivated):
        # Habilitar funcionalidades de campaign para el partner
        partner_permissions = PartnerPermissions(
            partner_id=event.partner_id,
            can_create_campaigns=True,
            max_budget_limit=10000.00
        )
        await self.repository.save(partner_permissions)
```

#### **3.2 API Síncronas para Queries**

##### **Profile 360 API (Partner Management)**
```python
# src/partner_management/api/partners_query.py
@partners_query_bp.route("/<partner_id>/profile-360", methods=["GET"])
@jwt_required()
def get_partner_profile_360(partner_id):
    try:
        # Obtener datos de partner
        partner = partner_query_service.get_by_id(partner_id)
        
        # Llamadas a otros servicios
        campaigns = campaign_service.get_partner_campaigns(partner_id)
        contracts = onboarding_service.get_partner_contracts(partner_id)
        jobs = recruitment_service.get_partner_jobs(partner_id)
        
        profile_360 = {
            "partner": partner,
            "campaigns": campaigns,
            "contracts": contracts,
            "recruitment": jobs,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return jsonify(profile_360), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

### **Fase 4: Testing y Validación (Semanas 9-10)**

#### **4.1 Tests de Migración**
```python
# tests/migration/test_campaign_extraction.py
class TestCampaignMigration:
    
    def test_campaign_data_integrity(self):
        # Verificar que todos los datos se migraron correctamente
        original_count = self.get_original_campaign_count()
        migrated_count = self.get_migrated_campaign_count()
        assert original_count == migrated_count
    
    def test_campaign_functionality(self):
        # Verificar que funcionalidades siguen trabajando
        campaign = self.create_test_campaign()
        assert campaign.id is not None
        assert campaign.estado == "ACTIVE"
    
    def test_events_integration(self):
        # Verificar comunicación entre servicios
        partner_event = PartnerRegistrationCompleted(
            partner_id="test-123",
            partner_data={"name": "Test Partner"}
        )
        
        # Verificar que Onboarding recibe el evento
        assert self.onboarding_received_event(partner_event)
```

#### **4.2 Tests de Rendimiento**
```python
# tests/performance/test_migration_performance.py
import time
import pytest

class TestMigrationPerformance:
    
    @pytest.mark.performance
    def test_partner_profile_360_response_time(self):
        start_time = time.time()
        
        response = self.client.get("/partners/test-123/profile-360")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5  # Menos de 500ms
    
    @pytest.mark.performance  
    def test_event_processing_latency(self):
        event_sent = time.time()
        
        # Enviar evento
        self.send_partner_registration_event()
        
        # Verificar procesamiento
        while not self.contract_created() and time.time() - event_sent < 5:
            time.sleep(0.1)
        
        processing_time = time.time() - event_sent
        assert processing_time < 2.0  # Menos de 2 segundos
```

---

### **Fase 5: Despliegue Gradual (Semanas 11-12)**

#### **5.1 Blue-Green Deployment**

##### **Configuración Blue Environment (Actual)**
```yaml
# docker-compose.blue.yml
version: '3.8'
services:
  partner-management-blue:
    image: hexabuilders/partner-management:current
    ports:
      - "5000:5000"
    environment:
      - ENV=blue
      - DATABASE_URL=postgresql://user:pass@postgres:5432/hexabuilders_blue
```

##### **Configuración Green Environment (Migrado)**
```yaml
# docker-compose.green.yml  
version: '3.8'
services:
  partner-management-green:
    image: hexabuilders/partner-management:migrated
    ports:
      - "5100:5000"
      
  onboarding-green:
    image: hexabuilders/onboarding:latest
    ports:
      - "5101:5000"
      
  recruitment-green:
    image: hexabuilders/recruitment:latest
    ports:
      - "5102:5000"
      
  campaign-management-green:
    image: hexabuilders/campaign-management:latest
    ports:
      - "5103:5000"
```

#### **5.2 Traffic Switching**
```bash
# Gradual traffic switching
# 10% traffic to green
./scripts/switch-traffic.sh --green-percentage=10

# Monitor for 1 hour
./scripts/monitor-migration.sh --duration=3600

# 50% traffic to green  
./scripts/switch-traffic.sh --green-percentage=50

# Monitor for 2 hours
./scripts/monitor-migration.sh --duration=7200

# 100% traffic to green
./scripts/switch-traffic.sh --green-percentage=100

# Verify and cleanup blue
./scripts/cleanup-blue-environment.sh
```

---

## 🚨 Plan de Rollback

### **Rollback Automático**
```bash
#!/bin/bash
# scripts/emergency-rollback.sh

echo "🚨 EMERGENCY ROLLBACK INITIATED"

# 1. Switch traffic back to blue
docker-compose -f docker-compose.blue.yml up -d
./scripts/switch-traffic.sh --green-percentage=0

# 2. Restore database if needed
if [ "$1" == "--restore-db" ]; then
    echo "Restoring database..."
    psql hexabuilders < backup_pre_migration.sql
fi

# 3. Verify blue environment
./scripts/health-check.sh --environment=blue

echo "✅ Rollback completed"
```

### **Criterios de Rollback**
- Error rate > 5%
- Response time > 1 segundo
- Pérdida de datos detectada
- Fallos en integraciones críticas

---

## 📊 Monitoreo Post-Migración

### **Métricas Clave**
```yaml
# monitoring/migration-alerts.yml
alerts:
  - name: MigrationErrorRate
    condition: error_rate > 0.05
    duration: 2m
    action: trigger_rollback
    
  - name: CrossServiceLatency
    condition: p95_latency > 1000ms
    duration: 5m
    action: alert_team
    
  - name: EventProcessingLag
    condition: event_lag > 30s
    duration: 1m
    action: scale_consumers

  - name: DataInconsistency
    condition: data_integrity_check == false
    duration: 0s
    action: immediate_investigation
```

### **Dashboard de Migración**
- **Business Metrics**: Partners activos, campañas creadas, contratos firmados
- **Technical Metrics**: Response times, error rates, event lag
- **Infrastructure**: CPU, memoria, conexiones DB
- **Integration**: Health checks entre servicios

---

## ✅ Checklist de Migración

### **Pre-Migración**
- [ ] Backup completo de base de datos
- [ ] Tests de migración pasando
- [ ] Entorno de staging configurado
- [ ] Plan de rollback validado
- [ ] Monitoreo configurado

### **Durante Migración**
- [ ] Blue environment funcionando
- [ ] Green environment deployado
- [ ] Data migration ejecutada
- [ ] Event flows configurados
- [ ] APIs síncronas funcionando

### **Post-Migración**
- [ ] Todas las métricas dentro del SLA
- [ ] Tests E2E pasando
- [ ] No hay data loss
- [ ] Performance igual o mejor
- [ ] Blue environment limpiado

---

Esta guía proporciona un enfoque estructurado y seguro para migrar de una arquitectura monolítica a microservicios, minimizando riesgos y asegurando continuidad del servicio.