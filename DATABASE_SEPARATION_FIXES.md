# Database Separation Deployment Fixes

## 🔧 Issues Fixed

### 1. **Fixed Kubernetes Deployment Files**

#### **Onboarding Service**
- ✅ Fixed port configuration: Changed from 5000 to 5001
- ✅ Added missing `SERVICE_PORT` environment variable
- ✅ Updated all port references in health checks and services

#### **Created Missing Deployment Files**
- ✅ `k8s/database-separation/recruitment-deployment-separated.yaml`
- ✅ `k8s/database-separation/campaign-management-deployment-separated.yaml`

### 2. **Database Configuration**

#### **Created Missing SQL Initialization Files**
- ✅ `sql/recruitment_init.sql` - Complete recruitment service schema
- ✅ `sql/campaign_management_init.sql` - Complete campaign management schema

#### **Database Secrets Configuration**
All database secrets properly configured with Base64 encoded connection strings:
- ✅ `partner-db-secret.yaml` - Partner Management DB
- ✅ `onboarding-db-secret.yaml` - Onboarding DB  
- ✅ `recruitment-db-secret.yaml` - Recruitment DB
- ✅ `campaign-db-secret.yaml` - Campaign Management DB

### 3. **Infrastructure Files**
- ✅ Copied missing Pulsar and Elasticsearch files to database-separation directory
- ✅ Updated kustomization.yaml with all required resources

## 🗄️ Database Architecture

### **Separate Database Instances**
```
Production Environment:
├── partner-db-instance (Partner Management)
│   ├── Database: partner_management
│   ├── User: partner_user
│   └── Tables: partners, campaigns, commissions, analytics_reports, domain_events
│
├── onboarding-db-instance (Onboarding Service)
│   ├── Database: onboarding
│   ├── User: onboarding_user
│   └── Tables: contracts, documents, legal, negotiations, domain_events
│
├── recruitment-db-instance (Recruitment Service)
│   ├── Database: recruitment
│   ├── User: recruitment_user
│   └── Tables: candidates, jobs, applications, interviews, matching_scores, domain_events
│
└── campaign-db-instance (Campaign Management)
    ├── Database: campaign_management
    ├── User: campaign_user
    └── Tables: campaigns, budget_allocations, targeting_configs, performance_metrics, campaign_assets, domain_events
```

### **Service Port Configuration**
- **Partner Management**: Port 5000
- **Onboarding**: Port 5001  
- **Recruitment**: Port 5002
- **Campaign Management**: Port 5003

## 🚀 Deployment Instructions

### **For Development (Docker Compose)**
```bash
# Start with separate databases
docker-compose -f docker-compose.separated-databases.yml up -d

# Services will be available on:
# - Partner Management: http://localhost:5000
# - Onboarding: http://localhost:5001
# - Recruitment: http://localhost:5002
# - Campaign Management: http://localhost:5003

# Database ports:
# - Partner Management DB: localhost:5433
# - Onboarding DB: localhost:5434
# - Recruitment DB: localhost:5435
# - Campaign Management DB: localhost:5436
```

### **For Production (Kubernetes)**

#### **1. Create GCP Database Instances**
```bash
# Create separate Cloud SQL instances
./scripts/create-separate-databases-gcp.sh PROJECT_ID us-central1
```

#### **2. Update Database Connection Secrets**
```bash
# Update the secrets with actual connection strings from GCP
kubectl apply -f k8s/database-separation/partner-db-secret.yaml
kubectl apply -f k8s/database-separation/onboarding-db-secret.yaml
kubectl apply -f k8s/database-separation/recruitment-db-secret.yaml
kubectl apply -f k8s/database-separation/campaign-db-secret.yaml
```

#### **3. Initialize Databases**
```bash
# Initialize each database with its schema
psql -h <partner-db-ip> -U partner_user -d partner_management -f sql/partner_management_init.sql
psql -h <onboarding-db-ip> -U onboarding_user -d onboarding -f sql/onboarding_init.sql
psql -h <recruitment-db-ip> -U recruitment_user -d recruitment -f sql/recruitment_init.sql
psql -h <campaign-db-ip> -U campaign_user -d campaign_management -f sql/campaign_management_init.sql
```

#### **4. Deploy Services**
```bash
# Deploy with separate databases
kubectl apply -k k8s/database-separation/

# Verify deployment
kubectl get all -n hexabuilders
kubectl get secrets -n hexabuilders
```

## 🔍 Verification Steps

### **1. Check Service Health**
```bash
# Check all pods are running
kubectl get pods -n hexabuilders

# Check service endpoints
kubectl get services -n hexabuilders

# Test health endpoints
curl http://<service-ip>:5000/health  # Partner Management
curl http://<service-ip>:5001/health  # Onboarding
curl http://<service-ip>:5002/health  # Recruitment
curl http://<service-ip>:5003/health  # Campaign Management
```

### **2. Verify Database Connections**
```bash
# Check database connectivity from pods
kubectl exec -it <partner-management-pod> -n hexabuilders -- python -c "
import os
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('Partner DB connection: OK')
conn.close()
"
```

### **3. Test Cross-Service Communication**
```bash
# Test Profile 360° API (aggregates from all services)
curl http://<partner-management-ip>:5000/api/v1/partners-query/<partner-id>/profile-360
```

## ✅ Success Criteria

- [ ] All services start successfully with separate databases
- [ ] Each service connects to its dedicated database instance
- [ ] Health checks pass for all services
- [ ] Profile 360° API aggregates data correctly
- [ ] Integration events work across services
- [ ] No shared database dependencies remain

## 🔄 Rollback Plan

If issues arise:
```bash
# Revert to original shared database deployment
kubectl delete -k k8s/database-separation/
kubectl apply -k k8s/

# This will restore the shared PostgreSQL instance
```

## 📋 Files Modified/Created

### **New Deployment Files**
- `k8s/database-separation/recruitment-deployment-separated.yaml`
- `k8s/database-separation/campaign-management-deployment-separated.yaml`

### **Updated Deployment Files**
- `k8s/database-separation/onboarding-deployment-separated.yaml` (Fixed ports)

### **New Database Schema Files**
- `sql/recruitment_init.sql`
- `sql/campaign_management_init.sql`

### **Configuration Files**
- `docker-compose.separated-databases.yml` (Already existed, verified)
- `k8s/database-separation/kustomization.yaml` (Updated with missing resources)

---

**Note**: This implementation provides proper microservices database isolation while maintaining all existing functionality and improving security, performance, and maintainability.
