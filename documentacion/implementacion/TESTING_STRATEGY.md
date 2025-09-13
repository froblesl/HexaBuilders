# Estrategia de Testing - HexaBuilders

## 🎯 Filosofía de Testing

### **Principios Fundamentales**
- **Test-First Approach**: Tests como especificación del comportamiento
- **Testing Pyramid**: Priorizar tests unitarios, complementar con integración y E2E
- **Fail Fast**: Tests deben fallar rápidamente y dar feedback claro
- **Independent Tests**: Cada test debe ser independiente y poder ejecutarse en cualquier orden
- **Realistic Data**: Usar datos representativos del dominio de negocio

### **Cobertura de Testing**
```
📊 Distribución de Tests (Total: ~1500 tests)
├── Unit Tests (70% - ~1050 tests)
│   ├── Domain Logic: 600 tests
│   ├── Application Services: 300 tests
│   └── Infrastructure: 150 tests
├── Integration Tests (25% - ~375 tests)
│   ├── Database: 150 tests
│   ├── Events: 125 tests
│   └── APIs: 100 tests
└── E2E Tests (5% - ~75 tests)
    ├── User Journeys: 50 tests
    └── Cross-Service: 25 tests
```

---

## 🏗️ Arquitectura de Testing

### **Testing por Capas**

#### **1. Domain Layer Testing**
```python
# tests/unit/partner_management/dominio/test_entities.py
import pytest
from unittest.mock import Mock
from partner_management.modulos.partners.dominio.entidades import Partner
from partner_management.modulos.partners.dominio.excepciones import PartnerInvalidoError

class TestPartner:
    
    def test_crear_partner_valido(self):
        # Arrange
        datos_partner = {
            "nombre": "Tech Solutions Inc",
            "email": "contact@techsolutions.com",
            "telefono": "+1234567890",
            "tipo": "EMPRESA"
        }
        
        # Act
        partner = Partner.crear_partner(**datos_partner)
        
        # Assert
        assert partner.id is not None
        assert partner.nombre == "Tech Solutions Inc"
        assert partner.estado == "ACTIVO"
        assert partner.fecha_registro is not None
        assert len(partner.eventos) == 1  # PartnerCreado event
    
    def test_activar_partner_desde_pendiente(self):
        # Arrange
        partner = Partner.crear_partner(
            nombre="Test Partner", 
            email="test@test.com",
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        partner.estado = "PENDIENTE"
        partner.eventos.clear()
        
        # Act
        partner.activar()
        
        # Assert
        assert partner.estado == "ACTIVO"
        assert len(partner.eventos) == 1
        assert partner.eventos[0].__class__.__name__ == "PartnerActivado"
    
    def test_no_puede_activar_partner_suspendido(self):
        # Arrange
        partner = Partner.crear_partner(
            nombre="Test Partner",
            email="test@test.com", 
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        partner.estado = "SUSPENDIDO"
        
        # Act & Assert
        with pytest.raises(PartnerInvalidoError) as exc_info:
            partner.activar()
        
        assert "no puede ser activado desde estado SUSPENDIDO" in str(exc_info.value)

    def test_calcular_score_credibilidad(self):
        # Arrange
        partner = Partner.crear_partner(
            nombre="Reliable Partner",
            email="reliable@partner.com",
            telefono="+1234567890", 
            tipo="EMPRESA"
        )
        
        # Simular historial
        partner.completar_campaña_exitosa()
        partner.completar_campaña_exitosa()
        partner.establecer_referencias_verificadas(5)
        
        # Act
        score = partner.calcular_score_credibilidad()
        
        # Assert
        assert 70 <= score <= 100  # Score alto por buen historial
```

#### **2. Application Services Testing**
```python
# tests/unit/partner_management/aplicacion/test_commands.py
import pytest
from unittest.mock import Mock, AsyncMock
from partner_management.modulos.partners.aplicacion.comandos import CrearPartner
from partner_management.modulos.partners.aplicacion.handlers import CrearPartnerHandler

class TestCrearPartnerHandler:
    
    @pytest.fixture
    def mock_dependencies(self):
        return {
            'repository': Mock(),
            'uow': Mock(),
            'event_bus': AsyncMock(),
            'validation_service': Mock()
        }
    
    @pytest.mark.asyncio
    async def test_crear_partner_exitoso(self, mock_dependencies):
        # Arrange
        comando = CrearPartner(
            nombre="New Partner",
            email="new@partner.com",
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        
        handler = CrearPartnerHandler(**mock_dependencies)
        mock_dependencies['validation_service'].validar_email.return_value = True
        mock_dependencies['validation_service'].validar_telefono.return_value = True
        
        # Act
        result = await handler.handle(comando)
        
        # Assert
        assert result.partner_id is not None
        mock_dependencies['repository'].save.assert_called_once()
        mock_dependencies['uow'].commit.assert_called_once()
        mock_dependencies['event_bus'].publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_crear_partner_email_duplicado(self, mock_dependencies):
        # Arrange
        comando = CrearPartner(
            nombre="Duplicate Partner",
            email="existing@partner.com",
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        
        handler = CrearPartnerHandler(**mock_dependencies)
        mock_dependencies['repository'].get_by_email.return_value = Mock()  # Partner existente
        
        # Act & Assert
        with pytest.raises(PartnerYaExisteError):
            await handler.handle(comando)
        
        mock_dependencies['repository'].save.assert_not_called()
        mock_dependencies['uow'].commit.assert_not_called()
```

#### **3. Infrastructure Testing**
```python
# tests/unit/partner_management/infraestructura/test_repositories.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from partner_management.seedwork.infraestructura.database import Base
from partner_management.modulos.partners.infraestructura.repositories import SqlAlchemyPartnerRepository

class TestSqlAlchemyPartnerRepository:
    
    @pytest.fixture
    def db_session(self):
        # In-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def repository(self, db_session):
        return SqlAlchemyPartnerRepository(db_session)
    
    @pytest.mark.asyncio
    async def test_save_and_get_partner(self, repository):
        # Arrange
        partner = Partner.crear_partner(
            nombre="Test Partner",
            email="test@repository.com",
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        
        # Act
        await repository.save(partner)
        retrieved_partner = await repository.get_by_id(partner.id)
        
        # Assert
        assert retrieved_partner is not None
        assert retrieved_partner.id == partner.id
        assert retrieved_partner.nombre == partner.nombre
        assert retrieved_partner.email == partner.email
    
    @pytest.mark.asyncio
    async def test_get_by_email_existing(self, repository):
        # Arrange
        partner = Partner.crear_partner(
            nombre="Email Test",
            email="email@test.com",
            telefono="+1234567890",
            tipo="INDIVIDUAL"
        )
        await repository.save(partner)
        
        # Act
        found_partner = await repository.get_by_email("email@test.com")
        
        # Assert
        assert found_partner is not None
        assert found_partner.email == "email@test.com"
    
    @pytest.mark.asyncio
    async def test_search_partners_by_criteria(self, repository):
        # Arrange - Crear varios partners
        partners = [
            Partner.crear_partner(f"Partner {i}", f"partner{i}@test.com", "+123456789{i}", "INDIVIDUAL")
            for i in range(5)
        ]
        
        for partner in partners:
            await repository.save(partner)
        
        # Act
        results = await repository.search(
            criterios={"tipo": "INDIVIDUAL"},
            limite=3,
            offset=1
        )
        
        # Assert
        assert len(results) == 3
        assert all(p.tipo == "INDIVIDUAL" for p in results)
```

---

## 🔗 Integration Testing

### **Database Integration Tests**
```python
# tests/integration/database/test_partner_persistence.py
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from partner_management.seedwork.infraestructura.database import Base
from partner_management.modulos.partners.infraestructura.repositories import SqlAlchemyPartnerRepository

@pytest.mark.integration
class TestPartnerPersistenceIntegration:
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        with PostgresContainer("postgres:15-alpine") as postgres:
            yield postgres
    
    @pytest.fixture
    def db_engine(self, postgres_container):
        connection_url = postgres_container.get_connection_url()
        engine = create_engine(connection_url)
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def repository(self, db_engine):
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=db_engine)
        session = Session()
        return SqlAlchemyPartnerRepository(session)
    
    @pytest.mark.asyncio
    async def test_partner_crud_operations(self, repository):
        # Create
        partner = Partner.crear_partner(
            nombre="Integration Test Partner",
            email="integration@test.com",
            telefono="+1234567890",
            tipo="EMPRESA"
        )
        
        await repository.save(partner)
        partner_id = partner.id
        
        # Read
        retrieved = await repository.get_by_id(partner_id)
        assert retrieved.nombre == "Integration Test Partner"
        
        # Update
        retrieved.actualizar_informacion(nombre="Updated Partner Name")
        await repository.save(retrieved)
        
        updated = await repository.get_by_id(partner_id)
        assert updated.nombre == "Updated Partner Name"
        
        # Delete
        await repository.delete(partner_id)
        deleted = await repository.get_by_id(partner_id)
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_partner_search_complex_queries(self, repository):
        # Arrange - Crear datos de prueba
        test_data = [
            {"nombre": "Tech Corp", "tipo": "EMPRESA", "sector": "TECHNOLOGY"},
            {"nombre": "Marketing Pro", "tipo": "INDIVIDUAL", "sector": "MARKETING"}, 
            {"nombre": "Design Studio", "tipo": "EMPRESA", "sector": "DESIGN"},
        ]
        
        for data in test_data:
            partner = Partner.crear_partner(
                nombre=data["nombre"],
                email=f"{data['nombre'].lower().replace(' ', '')}@test.com",
                telefono="+1234567890",
                tipo=data["tipo"]
            )
            partner.sector = data["sector"]
            await repository.save(partner)
        
        # Act & Assert - Búsqueda por tipo
        empresas = await repository.search(criterios={"tipo": "EMPRESA"})
        assert len(empresas) == 2
        
        # Búsqueda por sector
        tech_partners = await repository.search(criterios={"sector": "TECHNOLOGY"})
        assert len(tech_partners) == 1
        assert tech_partners[0].nombre == "Tech Corp"
```

### **Event Integration Tests**
```python
# tests/integration/events/test_event_flow.py
import pytest
import asyncio
from testcontainers.compose import DockerCompose
from partner_management.seedwork.infraestructura.pulsar import PulsarEventBus
from partner_management.modulos.partners.dominio.eventos import PartnerCreado

@pytest.mark.integration
@pytest.mark.slow
class TestEventIntegration:
    
    @pytest.fixture(scope="class")
    def pulsar_container(self):
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            compose.wait_for("http://localhost:8080/admin/v2/clusters")
            yield compose
    
    @pytest.fixture
    def event_bus(self, pulsar_container):
        return PulsarEventBus("pulsar://localhost:6650")
    
    @pytest.mark.asyncio
    async def test_publish_and_consume_partner_event(self, event_bus):
        # Arrange
        evento = PartnerCreado(
            partner_id="test-123",
            nombre="Test Partner",
            email="test@partner.com"
        )
        
        received_events = []
        
        async def event_handler(event):
            received_events.append(event)
        
        # Act
        await event_bus.subscribe("partner.created", event_handler)
        await event_bus.publish(evento)
        
        # Wait for event processing
        await asyncio.sleep(2)
        
        # Assert
        assert len(received_events) == 1
        assert received_events[0].partner_id == "test-123"
        assert received_events[0].nombre == "Test Partner"
    
    @pytest.mark.asyncio
    async def test_cross_service_event_flow(self, event_bus):
        # Simular flujo: Partner Management → Onboarding → Campaign Management
        
        events_received = {
            "partner_created": [],
            "contract_signed": [],
            "campaigns_enabled": []
        }
        
        # Suscribirse a eventos
        await event_bus.subscribe("partner.created", 
                                lambda e: events_received["partner_created"].append(e))
        await event_bus.subscribe("contract.signed",
                                lambda e: events_received["contract_signed"].append(e))
        await event_bus.subscribe("campaigns.enabled",
                                lambda e: events_received["campaigns_enabled"].append(e))
        
        # Simular flujo completo
        partner_event = PartnerCreado(partner_id="flow-test-123")
        await event_bus.publish(partner_event)
        
        # Simular respuesta de Onboarding
        await asyncio.sleep(1)
        contract_event = ContractSigned(partner_id="flow-test-123", contract_id="contract-456")
        await event_bus.publish(contract_event)
        
        # Simular respuesta de Campaign Management
        await asyncio.sleep(1)
        campaigns_event = CampaignsEnabled(partner_id="flow-test-123")
        await event_bus.publish(campaigns_event)
        
        # Wait for all events to be processed
        await asyncio.sleep(3)
        
        # Assert
        assert len(events_received["partner_created"]) == 1
        assert len(events_received["contract_signed"]) == 1
        assert len(events_received["campaigns_enabled"]) == 1
```

### **API Integration Tests**
```python
# tests/integration/api/test_partner_api.py
import pytest
import requests
from testcontainers.compose import DockerCompose

@pytest.mark.integration
class TestPartnerAPIIntegration:
    
    @pytest.fixture(scope="class")
    def app_container(self):
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            compose.wait_for("http://localhost:5000/health")
            yield compose
    
    def test_create_partner_complete_flow(self, app_container):
        base_url = "http://localhost:5000"
        
        # 1. Crear partner
        partner_data = {
            "nombre": "API Test Partner",
            "email": "api@test.com",
            "telefono": "+1234567890",
            "tipo": "INDIVIDUAL"
        }
        
        response = requests.post(f"{base_url}/partners", json=partner_data)
        assert response.status_code == 202  # Comando aceptado
        
        command_id = response.json()["command_id"]
        
        # 2. Verificar procesamiento del comando
        import time
        time.sleep(2)  # Esperar procesamiento asíncrono
        
        # 3. Consultar partner creado
        partners_response = requests.get(f"{base_url}/partners-query")
        assert partners_response.status_code == 200
        
        partners = partners_response.json()["partners"]
        created_partner = next((p for p in partners if p["email"] == "api@test.com"), None)
        
        assert created_partner is not None
        assert created_partner["nombre"] == "API Test Partner"
        assert created_partner["estado"] == "ACTIVO"
    
    def test_partner_profile_360_integration(self, app_container):
        # Primero crear un partner
        partner_data = {
            "nombre": "Profile 360 Test",
            "email": "profile360@test.com",
            "telefono": "+1234567890",
            "tipo": "EMPRESA"
        }
        
        create_response = requests.post("http://localhost:5000/partners", json=partner_data)
        assert create_response.status_code == 202
        
        time.sleep(2)  # Esperar procesamiento
        
        # Obtener partners para conseguir el ID
        partners_response = requests.get("http://localhost:5000/partners-query")
        partners = partners_response.json()["partners"] 
        test_partner = next((p for p in partners if p["email"] == "profile360@test.com"), None)
        
        # Solicitar Profile 360
        profile_response = requests.get(
            f"http://localhost:5000/partners-query/{test_partner['id']}/profile-360"
        )
        
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        # Verificar estructura del perfil
        assert "partner" in profile
        assert "campaigns" in profile
        assert "contracts" in profile
        assert "recruitment" in profile
        assert profile["partner"]["email"] == "profile360@test.com"
```

---

## 🌍 End-to-End Testing

### **User Journey Tests**
```python
# tests/e2e/test_partner_onboarding_journey.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.e2e
class TestPartnerOnboardingJourney:
    
    @pytest.fixture
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_complete_partner_onboarding_flow(self, driver):
        """Test del flujo completo de onboarding de un partner"""
        
        # 1. Partner se registra
        driver.get("http://localhost:3000/register")
        
        driver.find_element(By.ID, "nombre").send_keys("E2E Test Partner")
        driver.find_element(By.ID, "email").send_keys("e2e@test.com")
        driver.find_element(By.ID, "telefono").send_keys("+1234567890")
        driver.find_element(By.ID, "tipo").send_keys("EMPRESA")
        
        driver.find_element(By.ID, "submit").click()
        
        # 2. Verificar redirección a página de confirmación
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "registration-success"))
        )
        
        success_message = driver.find_element(By.ID, "success-message").text
        assert "Partner registrado exitosamente" in success_message
        
        # 3. Verificar que se inició proceso de contrato
        # Simular navegación a dashboard de admin
        driver.get("http://localhost:3000/admin/contracts")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contracts-list"))
        )
        
        # Buscar contrato para el partner
        contracts = driver.find_elements(By.CSS_SELECTOR, ".contract-item")
        partner_contract = None
        for contract in contracts:
            if "e2e@test.com" in contract.text:
                partner_contract = contract
                break
        
        assert partner_contract is not None
        assert "DRAFT" in partner_contract.text
        
        # 4. Firmar contrato
        partner_contract.find_element(By.CLASS_NAME, "sign-button").click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signature-modal"))
        )
        
        driver.find_element(By.ID, "digital-signature").send_keys("E2E Test Signature")
        driver.find_element(By.ID, "confirm-signature").click()
        
        # 5. Verificar que campaigns están habilitadas
        driver.get("http://localhost:3000/partners/e2e@test.com/dashboard")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "create-campaign-button"))
        )
        
        create_button = driver.find_element(By.ID, "create-campaign-button")
        assert create_button.is_enabled()
```

### **Cross-Service E2E Tests**
```python
# tests/e2e/test_cross_service_flows.py
import pytest
import asyncio
import requests
from partner_management.seedwork.infraestructura.pulsar import PulsarEventBus

@pytest.mark.e2e
@pytest.mark.slow
class TestCrossServiceFlows:
    
    @pytest.fixture
    def services_endpoints(self):
        return {
            "partner_management": "http://localhost:5000",
            "onboarding": "http://localhost:5001", 
            "recruitment": "http://localhost:5002",
            "campaign_management": "http://localhost:5003"
        }
    
    @pytest.mark.asyncio
    async def test_partner_to_campaign_creation_flow(self, services_endpoints):
        """Test del flujo: Crear Partner → Firmar Contrato → Crear Campaña"""
        
        # 1. Crear partner en Partner Management
        partner_data = {
            "nombre": "Flow Test Partner",
            "email": "flow@test.com",
            "telefono": "+1234567890",
            "tipo": "EMPRESA"
        }
        
        partner_response = requests.post(
            f"{services_endpoints['partner_management']}/partners",
            json=partner_data
        )
        assert partner_response.status_code == 202
        
        # Esperar procesamiento
        await asyncio.sleep(3)
        
        # 2. Verificar que el contrato se creó en Onboarding
        contracts_response = requests.get(
            f"{services_endpoints['onboarding']}/contracts-query",
            params={"partner_email": "flow@test.com"}
        )
        assert contracts_response.status_code == 200
        
        contracts = contracts_response.json()["contracts"]
        assert len(contracts) == 1
        assert contracts[0]["estado"] == "DRAFT"
        
        contract_id = contracts[0]["id"]
        
        # 3. Firmar contrato en Onboarding
        sign_response = requests.post(
            f"{services_endpoints['onboarding']}/contracts/{contract_id}/sign",
            json={"signature": "Test Signature", "signatory": "flow@test.com"}
        )
        assert sign_response.status_code == 202
        
        # Esperar procesamiento
        await asyncio.sleep(3)
        
        # 4. Verificar que campaigns están habilitadas en Campaign Management
        permissions_response = requests.get(
            f"{services_endpoints['campaign_management']}/permissions-query",
            params={"partner_email": "flow@test.com"}
        )
        assert permissions_response.status_code == 200
        
        permissions = permissions_response.json()["permissions"]
        assert permissions["can_create_campaigns"] is True
        
        # 5. Crear campaña
        campaign_data = {
            "nombre": "Test Campaign",
            "descripcion": "E2E Test Campaign",
            "presupuesto": 5000.00,
            "partner_email": "flow@test.com"
        }
        
        campaign_response = requests.post(
            f"{services_endpoints['campaign_management']}/campaigns",
            json=campaign_data
        )
        assert campaign_response.status_code == 202
        
        # Esperar procesamiento
        await asyncio.sleep(2)
        
        # 6. Verificar campaña creada
        campaigns_response = requests.get(
            f"{services_endpoints['campaign_management']}/campaigns-query",
            params={"partner_email": "flow@test.com"}
        )
        assert campaigns_response.status_code == 200
        
        campaigns = campaigns_response.json()["campaigns"]
        assert len(campaigns) == 1
        assert campaigns[0]["nombre"] == "Test Campaign"
        assert campaigns[0]["estado"] == "ACTIVE"
```

---

## 🚀 Performance Testing

### **Load Testing**
```python
# tests/performance/test_load.py
import asyncio
import pytest
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.performance
class TestLoadPerformance:
    
    @pytest.mark.asyncio
    async def test_partner_creation_load(self):
        """Test de carga para creación de partners"""
        
        async def create_partner(session, partner_id):
            partner_data = {
                "nombre": f"Load Test Partner {partner_id}",
                "email": f"load{partner_id}@test.com",
                "telefono": f"+123456789{partner_id}",
                "tipo": "INDIVIDUAL"
            }
            
            start_time = time.time()
            async with session.post("http://localhost:5000/partners", json=partner_data) as response:
                end_time = time.time()
                return {
                    "status": response.status,
                    "response_time": end_time - start_time,
                    "partner_id": partner_id
                }
        
        # Crear 100 partners concurrentemente
        async with aiohttp.ClientSession() as session:
            tasks = [create_partner(session, i) for i in range(100)]
            results = await asyncio.gather(*tasks)
        
        # Análisis de resultados
        successful_requests = [r for r in results if r["status"] == 202]
        response_times = [r["response_time"] for r in successful_requests]
        
        # Assertions
        assert len(successful_requests) >= 95  # 95% success rate
        assert max(response_times) < 2.0  # Ninguna request > 2s
        assert sum(response_times) / len(response_times) < 0.5  # Promedio < 500ms
    
    @pytest.mark.asyncio
    async def test_profile_360_performance(self):
        """Test de rendimiento para Profile 360 API"""
        
        # Primero crear un partner con datos completos
        partner_data = {
            "nombre": "Performance Test Partner",
            "email": "performance@test.com",
            "telefono": "+1234567890",
            "tipo": "EMPRESA"
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post("http://localhost:5000/partners", json=partner_data)
            await asyncio.sleep(2)  # Esperar procesamiento
            
            # Obtener partner ID
            async with session.get("http://localhost:5000/partners-query") as response:
                partners = await response.json()
                test_partner = next(p for p in partners["partners"] if p["email"] == "performance@test.com")
                partner_id = test_partner["id"]
            
            # Test de carga en Profile 360
            async def get_profile_360(session):
                start_time = time.time()
                async with session.get(f"http://localhost:5000/partners-query/{partner_id}/profile-360") as response:
                    end_time = time.time()
                    return {
                        "status": response.status,
                        "response_time": end_time - start_time
                    }
            
            # 50 requests concurrentes
            tasks = [get_profile_360(session) for _ in range(50)]
            results = await asyncio.gather(*tasks)
        
        # Análisis
        successful_requests = [r for r in results if r["status"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 48  # 96% success rate
        assert max(response_times) < 1.0  # Máximo 1 segundo
        assert sum(response_times) / len(response_times) < 0.3  # Promedio < 300ms
```

### **Stress Testing**
```python
# tests/performance/test_stress.py
import pytest
import locust
from locust import HttpUser, task, between

class PartnerManagementUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup que se ejecuta al iniciar cada usuario"""
        self.partner_id = None
    
    @task(3)
    def create_partner(self):
        """Crear partner - 30% del tráfico"""
        import random
        partner_data = {
            "nombre": f"Stress Test Partner {random.randint(1000, 9999)}",
            "email": f"stress{random.randint(1000, 9999)}@test.com",
            "telefono": f"+123456{random.randint(1000, 9999)}",
            "tipo": random.choice(["INDIVIDUAL", "EMPRESA"])
        }
        
        with self.client.post("/partners", json=partner_data, catch_response=True) as response:
            if response.status_code == 202:
                response.success()
            else:
                response.failure(f"Failed to create partner: {response.status_code}")
    
    @task(5)
    def get_partners(self):
        """Obtener lista de partners - 50% del tráfico"""
        with self.client.get("/partners-query", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get partners: {response.status_code}")
    
    @task(2)
    def get_profile_360(self):
        """Profile 360 - 20% del tráfico"""
        # Primero obtener un partner ID
        response = self.client.get("/partners-query")
        if response.status_code == 200:
            partners = response.json().get("partners", [])
            if partners:
                partner_id = partners[0]["id"]
                with self.client.get(f"/partners-query/{partner_id}/profile-360", catch_response=True) as profile_response:
                    if profile_response.status_code == 200:
                        profile_response.success()
                    else:
                        profile_response.failure(f"Failed to get profile 360: {profile_response.status_code}")

# Ejecutar: locust -f tests/performance/test_stress.py --host=http://localhost:5000
```

---

## 🔍 Testing Utilities

### **Test Data Factories**
```python
# tests/fixtures/factories.py
import factory
from faker import Faker
from partner_management.modulos.partners.dominio.entidades import Partner

fake = Faker()

class PartnerFactory(factory.Factory):
    class Meta:
        model = Partner
    
    nombre = factory.LazyFunction(lambda: fake.company())
    email = factory.LazyFunction(lambda: fake.email())
    telefono = factory.LazyFunction(lambda: fake.phone_number())
    tipo = factory.Iterator(["INDIVIDUAL", "EMPRESA"])
    sector = factory.Iterator(["TECHNOLOGY", "MARKETING", "DESIGN", "FINANCE"])
    
    @factory.post_generation
    def set_estado(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.estado = "ACTIVO"

class CampaignFactory(factory.Factory):
    class Meta:
        model = Campaign
    
    nombre = factory.LazyFunction(lambda: f"Campaña {fake.catch_phrase()}")
    descripcion = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    presupuesto = factory.LazyFunction(lambda: fake.pydecimal(left_digits=5, right_digits=2, positive=True))
    fecha_inicio = factory.LazyFunction(lambda: fake.date_this_month())
    fecha_fin = factory.LazyFunction(lambda: fake.date_this_year())

# Uso en tests
def test_with_factory_data():
    partner = PartnerFactory()
    campaign = CampaignFactory(partner=partner)
    assert partner.nombre is not None
    assert campaign.partner == partner
```

### **Test Helpers**
```python
# tests/helpers/assertions.py
def assert_partner_data_equals(partner1, partner2, ignore_fields=None):
    """Helper para comparar datos de partners"""
    ignore_fields = ignore_fields or ["id", "created_at", "updated_at"]
    
    for field in ["nombre", "email", "telefono", "tipo", "estado"]:
        if field not in ignore_fields:
            assert getattr(partner1, field) == getattr(partner2, field), f"Field {field} differs"

def assert_event_published(event_bus_mock, event_type, **expected_attrs):
    """Helper para verificar que un evento fue publicado"""
    published_events = [call.args[0] for call in event_bus_mock.publish.call_args_list]
    matching_events = [e for e in published_events if isinstance(e, event_type)]
    
    assert len(matching_events) > 0, f"No {event_type.__name__} event was published"
    
    if expected_attrs:
        for attr, value in expected_attrs.items():
            assert getattr(matching_events[0], attr) == value

def assert_api_response_structure(response_json, expected_structure):
    """Helper para verificar estructura de respuesta API"""
    def check_structure(data, structure):
        if isinstance(structure, dict):
            assert isinstance(data, dict)
            for key, value_type in structure.items():
                assert key in data, f"Missing key: {key}"
                check_structure(data[key], value_type)
        elif isinstance(structure, list):
            assert isinstance(data, list)
            if len(structure) > 0:
                for item in data:
                    check_structure(item, structure[0])
        else:
            assert isinstance(data, structure), f"Expected {structure}, got {type(data)}"
    
    check_structure(response_json, expected_structure)
```

---

## 📊 Test Reporting y Métricas

### **Coverage Configuration**
```ini
# .coveragerc
[run]
source = src
omit = 
    tests/*
    */migrations/*
    */venv/*
    */node_modules/*
    */test_*
    */__pycache__/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### **CI/CD Integration**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_hexabuilders
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      pulsar:
        image: apachepulsar/pulsar:3.1.0
        ports:
          - 8080:8080
          - 6650:6650
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r dev-requirements.txt
    
    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration/ -v -m "not slow"
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: coverage.xml
```

---

Esta estrategia de testing proporciona una cobertura completa y robusta para el sistema HexaBuilders, asegurando calidad, confiabilidad y mantenibilidad del código en todos los niveles.