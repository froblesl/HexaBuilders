# Configuración Apache Pulsar - HexaBuilders

## 🎯 Visión General

Apache Pulsar actúa como el **Event Backbone** de la arquitectura de microservicios de HexaBuilders, proporcionando:

- 📡 **Message Broker** de alta disponibilidad
- 🗃️ **Schema Registry** para versionado de eventos
- 🔄 **Multi-tenancy** nativo para aislamiento
- 📊 **Geo-replication** para disaster recovery
- ⚡ **High throughput** y baja latencia

---

## 🏗️ Arquitectura del Cluster Pulsar

```
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Pulsar Cluster                       │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   ZooKeeper     │    BookKeeper   │     Broker      │  Schema   │
│   (Metadata)    │   (Storage)     │   (Serving)     │ Registry  │
├─────────────────┼─────────────────┼─────────────────┼───────────┤
│ • Configuration │ • Event Storage │ • Producer API  │ • Avro    │
│ • Topic Metadata│ • Durability    │ • Consumer API  │ • JSON    │
│ • Partitioning  │ • Replication   │ • Load Balance  │ • Proto   │
│ • Leadership    │ • Tiered Storage│ • Auth & ACL    │ • Evolve  │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

---

## 🐳 Docker Compose Configuration

### **Actualización del docker-compose.yml**
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: hexabuilders-postgres
    profiles: ["database", "full"]
    environment:
      POSTGRES_DB: hexabuilders
      POSTGRES_USER: hexabuilders_user
      POSTGRES_PASSWORD: hexabuilders_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - hexabuilders
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hexabuilders_user -d hexabuilders"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Apache Pulsar Services
  zookeeper:
    image: apachepulsar/pulsar:3.1.0
    profiles: ["pulsar", "full"]
    container_name: hexabuilders-zookeeper
    hostname: zookeeper
    restart: unless-stopped
    networks:
      - hexabuilders
    volumes:
      - pulsar_data:/pulsar/data
      - pulsar_conf:/pulsar/conf
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
      - PULSAR_MEM=-Xms512m -Xmx512m -XX:MaxDirectMemorySize=256m
    command: >
      bash -c "bin/apply-config-from-env.py conf/zookeeper.conf && \
               bin/generate-zookeeper-config.sh conf/zookeeper.conf && \
               exec bin/pulsar zookeeper"
    healthcheck:
      test: ["CMD", "bin/pulsar-zookeeper-ruok.sh"]
      interval: 10s
      timeout: 5s
      retries: 30

  pulsar-init:
    image: apachepulsar/pulsar:3.1.0
    profiles: ["pulsar", "full"]
    container_name: hexabuilders-pulsar-init
    hostname: pulsar-init
    networks:
      - hexabuilders
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
    command: >
      bash -c "bin/apply-config-from-env.py conf/client.conf && \
               until nslookup zookeeper; do sleep 3; done && \
               bin/pulsar initialize-cluster-metadata \
                 --cluster hexabuilders-cluster \
                 --zookeeper zookeeper:2181 \
                 --configuration-store zookeeper:2181 \
                 --web-service-url http://broker:8080 \
                 --broker-service-url pulsar://broker:6650"
    depends_on:
      zookeeper:
        condition: service_healthy

  bookie:
    image: apachepulsar/pulsar:3.1.0
    profiles: ["pulsar", "full"]
    container_name: hexabuilders-bookie
    hostname: bookie
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - clusterName=hexabuilders-cluster
      - zkServers=zookeeper:2181
      - metadataServiceUri=metadata-store:zk:zookeeper:2181
      - advertisedAddress=bookie
      - PULSAR_MEM=-Xms1g -Xmx1g -XX:MaxDirectMemorySize=1g
    depends_on:
      zookeeper:
        condition: service_healthy
      pulsar-init:
        condition: service_completed_successfully
    volumes:
      - pulsar_data:/pulsar/data
      - pulsar_conf:/pulsar/conf
    command: >
      bash -c "bin/apply-config-from-env.py conf/bookkeeper.conf && \
               bin/apply-config-from-env.py conf/pulsar_env.sh && \
               exec bin/pulsar bookie"

  broker:
    image: apachepulsar/pulsar:3.1.0
    profiles: ["pulsar", "full"]
    container_name: hexabuilders-broker
    hostname: broker
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
      - zookeeperServers=zookeeper:2181
      - clusterName=hexabuilders-cluster
      - managedLedgerDefaultEnsembleSize=1
      - managedLedgerDefaultWriteQuorum=1
      - managedLedgerDefaultAckQuorum=1
      - advertisedAddress=broker
      - advertisedListeners=external:pulsar://127.0.0.1:6650
      - functionsWorkerEnabled=false
      - PULSAR_MEM=-Xms1g -Xmx1g -XX:MaxDirectMemorySize=1g
      # Schema Registry Configuration
      - schemaRegistryStorageClassName=org.apache.pulsar.broker.service.schema.BookkeeperSchemaStorageFactory
      - isSchemaValidationEnforced=true
      # Multi-tenancy Configuration  
      - authenticationEnabled=false
      - authorizationEnabled=false
      - superUserRoles=admin,pulsar-super
    depends_on:
      pulsar-init:
        condition: service_completed_successfully
      bookie:
        condition: service_started
    ports:
      - "6650:6650"  # Binary protocol
      - "8080:8080"  # HTTP Admin API
    volumes:
      - pulsar_data:/pulsar/data
      - pulsar_conf:/pulsar/conf
    command: >
      bash -c "bin/apply-config-from-env.py conf/broker.conf && \
               bin/apply-config-from-env.py conf/pulsar_env.sh && \
               exec bin/pulsar broker"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/admin/v2/brokers/health"]
      interval: 10s
      timeout: 5s
      retries: 30

  # Schema Registry (Standalone for development)
  pulsar-manager:
    image: apachepulsar/pulsar-manager:v0.3.0
    profiles: ["management", "full"]
    container_name: hexabuilders-pulsar-manager
    ports:
      - "9527:9527"  # Web UI
    environment:
      - SPRING_CONFIGURATION_FILE=/pulsar-manager/pulsar-manager/application.properties
    volumes:
      - pulsar_manager_data:/data
    networks:
      - hexabuilders
    depends_on:
      broker:
        condition: service_healthy

  # Microservices
  partner-management:
    build:
      context: .
      dockerfile: partner-management.Dockerfile
    container_name: hexabuilders-partner-management
    profiles: ["services", "full"]
    hostname: partner-management
    networks:
      - hexabuilders
    environment:
      - PULSAR_BROKER_URL=pulsar://broker:6650
      - PULSAR_ADMIN_URL=http://broker:8080
      - DATABASE_URL=postgresql://hexabuilders_user:hexabuilders_password@postgres:5432/hexabuilders
      - FLASK_ENV=development
      - SERVICE_NAME=partner-management
      - SERVICE_PORT=5000
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - broker
    volumes:
      - ./src:/app/src

  onboarding:
    build:
      context: .
      dockerfile: onboarding.Dockerfile
    container_name: hexabuilders-onboarding
    profiles: ["services", "full"]
    hostname: onboarding
    networks:
      - hexabuilders
    environment:
      - PULSAR_BROKER_URL=pulsar://broker:6650
      - PULSAR_ADMIN_URL=http://broker:8080
      - DATABASE_URL=postgresql://hexabuilders_user:hexabuilders_password@postgres:5432/hexabuilders
      - SERVICE_NAME=onboarding
      - SERVICE_PORT=5001
    ports:
      - "5001:5001"
    depends_on:
      - postgres
      - broker

  recruitment:
    build:
      context: .
      dockerfile: recruitment.Dockerfile
    container_name: hexabuilders-recruitment
    profiles: ["services", "full"]
    hostname: recruitment
    networks:
      - hexabuilders
    environment:
      - PULSAR_BROKER_URL=pulsar://broker:6650
      - PULSAR_ADMIN_URL=http://broker:8080
      - DATABASE_URL=postgresql://hexabuilders_user:hexabuilders_password@postgres:5432/hexabuilders
      - SERVICE_NAME=recruitment
      - SERVICE_PORT=5002
    ports:
      - "5002:5002"
    depends_on:
      - postgres
      - broker

  campaign-management:
    build:
      context: .
      dockerfile: campaign-management.Dockerfile
    container_name: hexabuilders-campaign-management
    profiles: ["services", "full"]
    hostname: campaign-management
    networks:
      - hexabuilders
    environment:
      - PULSAR_BROKER_URL=pulsar://broker:6650
      - PULSAR_ADMIN_URL=http://broker:8080
      - DATABASE_URL=postgresql://hexabuilders_user:hexabuilders_password@postgres:5432/hexabuilders
      - SERVICE_NAME=campaign-management
      - SERVICE_PORT=5003
    ports:
      - "5003:5003"
    depends_on:
      - postgres
      - broker

  notifications:
    build:
      context: .
      dockerfile: notifications.Dockerfile
    container_name: hexabuilders-notifications
    profiles: ["services", "full"]
    hostname: notifications
    networks:
      - hexabuilders
    environment:
      - PULSAR_BROKER_URL=pulsar://broker:6650
      - PULSAR_ADMIN_URL=http://broker:8080
      - SERVICE_NAME=notifications
    depends_on:
      - broker

networks:
  hexabuilders:
    driver: bridge
    name: hexabuilders-network

volumes:
  postgres_data:
    name: hexabuilders-postgres-data
  pulsar_data:
    name: hexabuilders-pulsar-data
  pulsar_conf:
    name: hexabuilders-pulsar-conf
  pulsar_manager_data:
    name: hexabuilders-pulsar-manager-data
```

---

## 🏷️ Namespace y Topic Structure

### **Namespaces por Servicio**
```bash
# Crear namespaces
pulsar-admin namespaces create hexabuilders/partner-management
pulsar-admin namespaces create hexabuilders/onboarding
pulsar-admin namespaces create hexabuilders/recruitment
pulsar-admin namespaces create hexabuilders/campaign-management
pulsar-admin namespaces create hexabuilders/notifications
pulsar-admin namespaces create hexabuilders/system
```

### **Topics Structure**
```
persistent://hexabuilders/{service}/{category}

Examples:
- persistent://hexabuilders/partner-management/partner-events
- persistent://hexabuilders/partner-management/partner-registration
- persistent://hexabuilders/onboarding/contract-events
- persistent://hexabuilders/onboarding/contract-signed
- persistent://hexabuilders/recruitment/candidate-events
- persistent://hexabuilders/recruitment/candidate-matched
- persistent://hexabuilders/campaign-management/campaign-events
- persistent://hexabuilders/campaign-management/performance-report
- persistent://hexabuilders/system/dead-letters
```

### **Topic Configuration**
```python
# Configuración estándar de topics
TOPIC_CONFIG = {
    'partitions': 4,  # Para paralelismo
    'retention_time_minutes': 7 * 24 * 60,  # 7 días
    'retention_size_mb': 1024,  # 1GB por partición
    'compression_type': 'LZ4',  # Compresión eficiente
    'deduplication_enabled': True,  # Deduplicación
    'schema_validation_enforced': True  # Validación de esquemas
}
```

---

## 📋 Schema Registry Configuration

### **Avro Schemas por Servicio**

#### **Partner Management Schemas**
```python
# Schema para PartnerRegistrationCompleted
PARTNER_REGISTRATION_SCHEMA = {
    "type": "record",
    "name": "PartnerRegistrationCompleted",
    "namespace": "com.hexabuilders.partners.events.v1",
    "fields": [
        {"name": "partner_id", "type": "string"},
        {"name": "business_name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "partner_type", "type": "string"},
        {"name": "registration_data", "type": "string"},  # JSON serializado
        {"name": "registration_timestamp", "type": "string"},
        {"name": "correlation_id", "type": "string"},
        {"name": "event_version", "type": "int", "default": 1}
    ]
}
```

#### **Onboarding Schemas**
```python
# Schema para ContractActivated
CONTRACT_ACTIVATED_SCHEMA = {
    "type": "record",
    "name": "ContractActivated",
    "namespace": "com.hexabuilders.onboarding.events.v1",
    "fields": [
        {"name": "contract_id", "type": "string"},
        {"name": "partner_id", "type": "string"},
        {"name": "contract_type", "type": "string"},
        {"name": "effective_date", "type": "string"},
        {"name": "campaign_permissions", "type": "string"},  # JSON array
        {"name": "budget_limits", "type": "string"},  # JSON object
        {"name": "correlation_id", "type": "string"},
        {"name": "event_version", "type": "int", "default": 1}
    ]
}
```

### **Schema Evolution Strategy**
```python
class SchemaVersionManager:
    def register_schema_evolution(self, topic: str, schema: dict, version: int):
        """
        Registrar evolución de esquema compatible hacia atrás
        """
        compatibility_rules = [
            "BACKWARD",     # Nuevos campos con defaults
            "FORWARD",      # Eliminar campos opcionales
            "FULL"          # Combinación de ambos
        ]
        
        return self.schema_registry.register(
            topic=topic,
            schema=schema,
            schema_type="AVRO",
            compatibility=compatibility_rules[2]  # FULL compatibility
        )
```

---

## 🔧 Client Configuration

### **Producer Configuration**
```python
class PulsarEventPublisher:
    def __init__(self, broker_url: str, schema_registry_url: str):
        self.client = pulsar.Client(
            service_url=broker_url,
            # Connection settings
            connection_timeout_ms=5000,
            operation_timeout_ms=30000,
            # Authentication (disabled for development)
            authentication=None,
            # TLS settings (disabled for development)
            use_tls=False,
            # Logger
            logger=pulsar.ConsoleLogger(pulsar.LogLevel.Info)
        )
        
        self.producers = {}
        
    async def create_producer(self, topic: str, schema: pulsar.schema.Schema):
        """Crear producer con configuración optimizada"""
        producer = self.client.create_producer(
            topic=topic,
            schema=schema,
            # Performance settings
            batching_enabled=True,
            batch_size=32,
            max_pending_messages=1000,
            # Delivery settings
            send_timeout_ms=30000,
            # Compression
            compression_type=pulsar.CompressionType.LZ4,
            # Partitioning
            partitions_routing_mode=pulsar.PartitionsRoutingMode.RoundRobinDistribution
        )
        
        self.producers[topic] = producer
        return producer
        
    async def publish_event(self, topic: str, event: IntegrationEvent):
        """Publicar evento con retry automático"""
        producer = self.producers.get(topic)
        if not producer:
            raise ValueError(f"Producer not configured for topic: {topic}")
            
        try:
            # Serializar evento a Cloud Events format
            cloud_event = event.to_cloud_event()
            
            # Publicar con metadatos
            producer.send(
                content=cloud_event,
                event_timestamp=int(time.time() * 1000),
                properties={
                    'correlation_id': event.metadata.correlation_id,
                    'event_type': event.__class__.__name__,
                    'source_service': os.getenv('SERVICE_NAME'),
                    'event_version': str(event.metadata.event_version)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise
```

### **Consumer Configuration**
```python
class PulsarEventConsumer:
    def __init__(self, broker_url: str, service_name: str):
        self.client = pulsar.Client(service_url=broker_url)
        self.service_name = service_name
        self.consumers = {}
        
    async def create_consumer(self, topic: str, subscription_name: str, 
                            event_handler: callable, schema: pulsar.schema.Schema):
        """Crear consumer con configuración robusta"""
        consumer = self.client.subscribe(
            topic=topic,
            subscription_name=f"{self.service_name}-{subscription_name}",
            schema=schema,
            # Subscription settings
            consumer_type=pulsar.ConsumerType.Shared,
            subscription_initial_position=pulsar.InitialPosition.Earliest,
            # Acknowledgment settings
            ack_timeout_ms=30000,
            negative_ack_redelivery_delay_ms=1000,
            # Retry settings
            max_redeliver_count=3,
            dead_letter_topic=f"{topic}-{self.service_name}-dlq",
            # Batch settings
            batch_receive_policy=pulsar.BatchReceivePolicy(
                max_num_messages=10,
                timeout_ms=5000
            )
        )
        
        self.consumers[topic] = {
            'consumer': consumer,
            'handler': event_handler
        }
        
        return consumer
        
    async def start_consuming(self, topic: str):
        """Iniciar consumo de eventos con manejo de errores"""
        consumer_info = self.consumers.get(topic)
        if not consumer_info:
            raise ValueError(f"Consumer not configured for topic: {topic}")
            
        consumer = consumer_info['consumer']
        handler = consumer_info['handler']
        
        while True:
            try:
                # Recibir mensaje
                msg = consumer.receive(timeout_ms=1000)
                
                # Deserializar evento
                event_data = msg.data()
                event = self.deserialize_event(event_data)
                
                # Procesar evento
                await handler(event)
                
                # Confirmar procesamiento
                consumer.acknowledge(msg)
                
            except pulsar.Timeout:
                # Timeout normal, continuar
                continue
            except Exception as e:
                logger.error(f"Error processing message from {topic}: {e}")
                # Negative acknowledge para reintento
                consumer.negative_acknowledge(msg)
```

---

## 🔒 Security Configuration (Production)

### **Authentication & Authorization**
```yaml
# broker.conf additions for production
authenticationEnabled=true
authorizationEnabled=true
authenticationProviders=org.apache.pulsar.broker.authentication.AuthenticationProviderToken
tokenSecretKey=file:///pulsar/conf/secret.key

# Superuser roles
superUserRoles=admin,service-account

# Authorization settings
authorizationProvider=org.apache.pulsar.broker.authorization.PulsarAuthorizationProvider
```

### **TLS Configuration**
```yaml
# TLS settings
brokerServicePortTls=6651
webServicePortTls=8443
tlsEnabled=true
tlsKeyFilePath=/pulsar/conf/broker-key.pem
tlsCertificateFilePath=/pulsar/conf/broker-cert.pem
tlsTrustCertsFilePath=/pulsar/conf/ca-cert.pem
```

---

## 📊 Monitoring & Observability

### **Prometheus Metrics**
```python
# Métricas personalizadas para eventos
from prometheus_client import Counter, Histogram, Gauge

# Métricas de producción
events_published_total = Counter(
    'pulsar_events_published_total',
    'Total events published',
    ['service', 'topic', 'event_type']
)

event_publish_duration = Histogram(
    'pulsar_event_publish_duration_seconds',
    'Event publish duration',
    ['service', 'topic']
)

# Métricas de consumo  
events_consumed_total = Counter(
    'pulsar_events_consumed_total',
    'Total events consumed',
    ['service', 'topic', 'subscription']
)

consumer_lag = Gauge(
    'pulsar_consumer_lag',
    'Consumer lag in messages',
    ['service', 'topic', 'subscription']
)
```

### **Health Checks**
```python
@app.route('/health/pulsar')
async def pulsar_health():
    """Health check para conectividad Pulsar"""
    try:
        # Test producer
        test_producer = pulsar_client.create_producer(
            f"persistent://hexabuilders/system/health-check",
            send_timeout_ms=5000
        )
        test_producer.close()
        
        # Test admin API
        admin_client = pulsar.PulsarAdmin(
            service_url='http://broker:8080'
        )
        namespaces = admin_client.namespaces().get_namespaces('hexabuilders')
        
        return jsonify({
            'pulsar_broker': 'healthy',
            'admin_api': 'healthy',
            'namespaces_count': len(namespaces)
        }), 200
        
    except Exception as e:
        return jsonify({
            'pulsar_broker': 'unhealthy',
            'error': str(e)
        }), 503
```

---

## 🚀 Deployment Commands

### **Development Environment**
```bash
# Iniciar solo Pulsar infrastructure
docker-compose --profile pulsar up -d

# Iniciar servicios individuales
docker-compose --profile services up partner-management

# Iniciar todo el stack
docker-compose --profile full up -d
```

### **Topic Management**
```bash
# Crear topics programáticamente
python scripts/create_topics.py

# Verificar topics
docker exec -it hexabuilders-broker pulsar-admin topics list hexabuilders

# Ver stats de topics
docker exec -it hexabuilders-broker pulsar-admin topics stats \
  persistent://hexabuilders/partner-management/partner-events
```

### **Schema Management**
```bash
# Listar esquemas
docker exec -it hexabuilders-broker pulsar-admin schemas list hexabuilders

# Ver esquema específico
docker exec -it hexabuilders-broker pulsar-admin schemas get \
  persistent://hexabuilders/partner-management/partner-registration
```

---

Esta configuración proporciona una base sólida y escalable para Apache Pulsar en el ecosistema HexaBuilders, con todas las características necesarias para soportar la arquitectura de microservicios basada en eventos.