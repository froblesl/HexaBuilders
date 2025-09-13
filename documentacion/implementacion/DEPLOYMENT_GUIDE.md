# Guía de Despliegue - HexaBuilders

## 🚀 Despliegue con Docker Compose

### **Pre-requisitos**
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM mínimo
- 20GB espacio en disco

### **Configuración del Entorno**

#### **Variables de Entorno**
```bash
# .env
# Database Configuration
POSTGRES_DB=hexabuilders
POSTGRES_USER=hexauser
POSTGRES_PASSWORD=hexapass123
DATABASE_URL=postgresql://hexauser:hexapass123@postgres:5432/hexabuilders

# Pulsar Configuration
PULSAR_SERVICE_URL=pulsar://broker:6650
PULSAR_WEB_SERVICE_URL=http://broker:8080

# Service Ports
PARTNER_MANAGEMENT_PORT=5000
ONBOARDING_PORT=5001
RECRUITMENT_PORT=5002
CAMPAIGN_MANAGEMENT_PORT=5003
NOTIFICATIONS_PORT=5004

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

#### **Docker Compose Completo**
```yaml
version: '3.8'

services:
  # Infrastructure Services
  zookeeper:
    image: apachepulsar/pulsar:3.1.0
    container_name: zookeeper
    restart: on-failure
    networks:
      - hexabuilders
    volumes:
      - zookeeper-data:/pulsar/data/zookeeper
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
      - PULSAR_MEM=-Xms256m -Xmx256m -XX:MaxDirectMemorySize=256m
    command: >
      bash -c "bin/apply-config-from-env.py conf/zookeeper.conf &&
               bin/generate-zookeeper-config.sh conf/zookeeper.conf &&
               exec bin/pulsar zookeeper"

  bookie:
    image: apachepulsar/pulsar:3.1.0
    container_name: bookie
    restart: on-failure
    networks:
      - hexabuilders
    environment:
      - clusterName=cluster-a
      - zkServers=zookeeper:2181
      - metadataServiceUri=metadata-store:zk:zookeeper:2181
      - advertisedAddress=bookie
      - BOOKIE_MEM=-Xms512m -Xmx512m -XX:MaxDirectMemorySize=256m
    depends_on:
      - zookeeper
    volumes:
      - bookie-data:/pulsar/data/bookkeeper
    command: >
      bash -c "bin/apply-config-from-env.py conf/bookkeeper.conf &&
               bin/bookkeeper shell metaformat &&
               exec bin/pulsar bookie"

  broker:
    image: apachepulsar/pulsar:3.1.0
    container_name: broker
    restart: on-failure
    networks:
      - hexabuilders
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
      - zookeeperServers=zookeeper:2181
      - clusterName=cluster-a
      - managedLedgerDefaultEnsembleSize=1
      - managedLedgerDefaultWriteQuorum=1
      - managedLedgerDefaultAckQuorum=1
      - advertisedAddress=broker
      - advertisedListeners=external:pulsar://127.0.0.1:6650
      - PULSAR_MEM=-Xms512m -Xmx512m -XX:MaxDirectMemorySize=256m
    depends_on:
      - zookeeper
      - bookie
    ports:
      - "6650:6650"
      - "8080:8080"
    volumes:
      - broker-data:/pulsar/data
    command: >
      bash -c "bin/apply-config-from-env.py conf/broker.conf &&
               exec bin/pulsar broker"

  pulsar-init:
    image: apachepulsar/pulsar:3.1.0
    container_name: pulsar-init
    networks:
      - hexabuilders
    environment:
      - metadataStoreUrl=zk:zookeeper:2181
    depends_on:
      - broker
    command: >
      bash -c "
        bin/pulsar initialize-cluster-metadata \
          --cluster cluster-a \
          --zookeeper zookeeper:2181 \
          --configuration-store zookeeper:2181 \
          --web-service-url http://broker:8080 \
          --broker-service-url pulsar://broker:6650
      "

  # Database
  postgres:
    image: postgres:15-alpine
    container_name: hexabuilders-postgres
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  # Application Services
  partner-management:
    build:
      context: .
      dockerfile: src/partner_management/Dockerfile
    container_name: partner-management
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_WEB_SERVICE_URL=${PULSAR_WEB_SERVICE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "${PARTNER_MANAGEMENT_PORT}:5000"
    depends_on:
      - postgres
      - broker
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  onboarding:
    build:
      context: .
      dockerfile: src/onboarding/Dockerfile
    container_name: onboarding
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_WEB_SERVICE_URL=${PULSAR_WEB_SERVICE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "${ONBOARDING_PORT}:5000"
    depends_on:
      - postgres
      - broker
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  recruitment:
    build:
      context: .
      dockerfile: src/recruitment/Dockerfile
    container_name: recruitment
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_WEB_SERVICE_URL=${PULSAR_WEB_SERVICE_URL}
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "${RECRUITMENT_PORT}:5000"
    depends_on:
      - postgres
      - broker
      - elasticsearch
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  campaign-management:
    build:
      context: .
      dockerfile: src/campaign_management/Dockerfile
    container_name: campaign-management
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_WEB_SERVICE_URL=${PULSAR_WEB_SERVICE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "${CAMPAIGN_MANAGEMENT_PORT}:5000"
    depends_on:
      - postgres
      - broker
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  notifications:
    build:
      context: .
      dockerfile: src/notificaciones/Dockerfile
    container_name: notifications
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL}
      - PULSAR_WEB_SERVICE_URL=${PULSAR_WEB_SERVICE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "${NOTIFICATIONS_PORT}:5000"
    depends_on:
      - postgres
      - broker
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Supporting Services
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    restart: unless-stopped
    networks:
      - hexabuilders
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

volumes:
  postgres-data:
  zookeeper-data:
  bookie-data:
  broker-data:
  elasticsearch-data:

networks:
  hexabuilders:
    driver: bridge
```

### **Scripts de Inicialización**

#### **init-db.sql**
```sql
-- Create databases for each service
CREATE DATABASE partner_management;
CREATE DATABASE onboarding;
CREATE DATABASE recruitment;
CREATE DATABASE campaign_management;
CREATE DATABASE notifications;

-- Create users with appropriate permissions
CREATE USER partner_user WITH ENCRYPTED PASSWORD 'partner_pass123';
CREATE USER onboarding_user WITH ENCRYPTED PASSWORD 'onboarding_pass123';
CREATE USER recruitment_user WITH ENCRYPTED PASSWORD 'recruitment_pass123';
CREATE USER campaign_user WITH ENCRYPTED PASSWORD 'campaign_pass123';
CREATE USER notifications_user WITH ENCRYPTED PASSWORD 'notifications_pass123';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE partner_management TO partner_user;
GRANT ALL PRIVILEGES ON DATABASE onboarding TO onboarding_user;
GRANT ALL PRIVILEGES ON DATABASE recruitment TO recruitment_user;
GRANT ALL PRIVILEGES ON DATABASE campaign_management TO campaign_user;
GRANT ALL PRIVILEGES ON DATABASE notifications TO notifications_user;
```

### **Comandos de Despliegue**

#### **Despliegue Completo**
```bash
# Crear archivo .env con las variables
cp .env.example .env

# Construir e iniciar todos los servicios
docker-compose up -d

# Verificar estado de servicios
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f partner-management
```

#### **Despliegue por Fases**
```bash
# Fase 1: Infraestructura
docker-compose up -d postgres zookeeper bookie broker pulsar-init elasticsearch

# Verificar infraestructura
docker-compose ps

# Fase 2: Servicios de aplicación
docker-compose up -d partner-management onboarding recruitment campaign-management notifications

# Verificar aplicaciones
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

### **Verificación del Despliegue**

#### **Health Checks**
```bash
# Script de verificación completa
#!/bin/bash
services=("5000" "5001" "5002" "5003" "5004")
for port in "${services[@]}"; do
  echo "Checking service on port $port..."
  curl -f http://localhost:$port/health || echo "Service on port $port is DOWN"
done

# Verificar Pulsar
curl -f http://localhost:8080/admin/v2/clusters

# Verificar PostgreSQL
docker exec hexabuilders-postgres psql -U hexauser -d hexabuilders -c "SELECT version();"

# Verificar Elasticsearch
curl -f http://localhost:9200/_cluster/health
```

#### **Monitoreo de Logs**
```bash
# Logs agregados con timestamps
docker-compose logs -f --timestamps

# Filtrar logs por nivel
docker-compose logs | grep ERROR
docker-compose logs | grep WARN

# Logs de un servicio con seguimiento
docker-compose logs -f partner-management --tail=50
```

---

## 🏭 Despliegue en Producción

### **Kubernetes Deployment**

#### **Namespace y ConfigMap**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hexabuilders

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: hexabuilders-config
  namespace: hexabuilders
data:
  PULSAR_SERVICE_URL: "pulsar://pulsar-broker:6650"
  PULSAR_WEB_SERVICE_URL: "http://pulsar-broker:8080"
  ELASTICSEARCH_URL: "http://elasticsearch:9200"
  LOG_LEVEL: "INFO"
```

#### **Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hexabuilders-secrets
  namespace: hexabuilders
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL2hleGF1c2VyOmhleGFwYXNzMTIzQHBvc3RncmVzOjU0MzIvaGV4YWJ1aWxkZXJz
  JWT_SECRET_KEY: eW91ci1zdXBlci1zZWNyZXQtand0LWtleS1jaGFuZ2UtaW4tcHJvZHVjdGlvbg==
```

#### **Deployment Example (Partner Management)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: partner-management
  namespace: hexabuilders
spec:
  replicas: 3
  selector:
    matchLabels:
      app: partner-management
  template:
    metadata:
      labels:
        app: partner-management
    spec:
      containers:
      - name: partner-management
        image: hexabuilders/partner-management:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hexabuilders-secrets
              key: DATABASE_URL
        - name: PULSAR_SERVICE_URL
          valueFrom:
            configMapKeyRef:
              name: hexabuilders-config
              key: PULSAR_SERVICE_URL
        livenessProbe:
          httpGet:
            path: /health/live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### **Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: partner-management-service
  namespace: hexabuilders
spec:
  selector:
    app: partner-management
  ports:
  - port: 80
    targetPort: 5000
  type: ClusterIP
```

### **Ingress Configuration**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hexabuilders-ingress
  namespace: hexabuilders
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.hexabuilders.com
    secretName: hexabuilders-tls
  rules:
  - host: api.hexabuilders.com
    http:
      paths:
      - path: /partners
        pathType: Prefix
        backend:
          service:
            name: partner-management-service
            port:
              number: 80
      - path: /onboarding
        pathType: Prefix
        backend:
          service:
            name: onboarding-service
            port:
              number: 80
```

---

## 📊 Monitoreo y Observabilidad

### **Prometheus Configuration**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hexabuilders-services'
    static_configs:
      - targets: ['partner-management:5000', 'onboarding:5001', 'recruitment:5002', 'campaign-management:5003']
    metrics_path: /metrics
    scrape_interval: 30s
```

### **Grafana Dashboards**
- **Service Health**: Uptime, response times, error rates
- **Business Metrics**: Partner registrations, campaigns created, contracts signed
- **Infrastructure**: Database connections, Pulsar message rates, memory usage

### **Alerting Rules**
```yaml
groups:
- name: hexabuilders-alerts
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "HexaBuilders service {{ $labels.instance }} is down"
      
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate on {{ $labels.instance }}"
```

---

## 🔧 Configuración de Desarrollo

### **Local Development Setup**
```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -r pulsar-requirements.txt

# Variables de entorno para desarrollo
export DATABASE_URL="postgresql://hexauser:hexapass123@localhost:5432/hexabuilders"
export PULSAR_SERVICE_URL="pulsar://localhost:6650"
export FLASK_ENV="development"
export LOG_LEVEL="DEBUG"

# Iniciar solo infraestructura
docker-compose up -d postgres broker elasticsearch

# Ejecutar servicio en modo desarrollo
cd src/partner_management && python -m api.partners
```

### **Testing Configuration**
```bash
# Variables para tests
export DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/test_hexabuilders"
export PULSAR_SERVICE_URL="pulsar://localhost:6650"

# Ejecutar tests
pytest tests/ -v --cov=src --cov-report=html

# Tests de integración
pytest tests/integration/ -v --slow
```

---

Esta guía proporciona todos los elementos necesarios para desplegar HexaBuilders en diferentes entornos, desde desarrollo local hasta producción en Kubernetes, incluyendo monitoreo y observabilidad completa.