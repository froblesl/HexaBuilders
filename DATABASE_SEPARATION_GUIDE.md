# Database Separation Implementation Guide

## 🎯 Overview

This guide implements **separate database instances** for each microservice in production, migrating from the current **schema separation** approach to proper **microservices database isolation**.

## 📊 Current vs Proposed Architecture

### **Current (Development)**
```
Single PostgreSQL Instance
├── public schema (Partner Management)
├── onboarding schema (Onboarding Service)
├── recruitment schema (Recruitment Service)
└── campaign_management schema (Campaign Management)
```

### **Proposed (Production)**
```
Separate Database Instances
├── partner-db-instance (Partner Management)
├── onboarding-db-instance (Onboarding Service)
├── recruitment-db-instance (Recruitment Service)
└── campaign-db-instance (Campaign Management)
```

## 🏗️ Implementation Files

### **1. Database Secrets**
- `k8s/database-separation/partner-db-secret.yaml`
- `k8s/database-separation/onboarding-db-secret.yaml`
- `k8s/database-separation/recruitment-db-secret.yaml`
- `k8s/database-separation/campaign-db-secret.yaml`

### **2. Updated Deployments**
- `k8s/database-separation/partner-management-deployment-separated.yaml`
- `k8s/database-separation/onboarding-deployment-separated.yaml`
- `k8s/database-separation/recruitment-deployment-separated.yaml`
- `k8s/database-separation/campaign-management-deployment-separated.yaml`

### **3. Database Initialization Scripts**
- `sql/partner_management_init.sql`
- `sql/onboarding_init.sql`
- `sql/recruitment_init.sql`
- `sql/campaign_management_init.sql`

### **4. Migration Scripts**
- `scripts/migrate-to-separate-databases.sh`
- `scripts/create-separate-databases-gcp.sh`

### **5. Docker Compose for Development**
- `docker-compose.separated-databases.yml`

## 🚀 Implementation Steps

### **Step 1: Create GCP Database Instances**

```bash
# Create separate Cloud SQL instances
./scripts/create-separate-databases-gcp.sh PROJECT_ID us-central1

# This creates:
# - partner-db-instance
# - onboarding-db-instance  
# - recruitment-db-instance
# - campaign-db-instance
```

### **Step 2: Update Kubernetes Secrets**

```bash
# Update secrets with actual connection strings
kubectl apply -f k8s/database-separation/partner-db-secret.yaml
kubectl apply -f k8s/database-separation/onboarding-db-secret.yaml
kubectl apply -f k8s/database-separation/recruitment-db-secret.yaml
kubectl apply -f k8s/database-separation/campaign-db-secret.yaml
```

### **Step 3: Initialize Databases**

```bash
# Initialize each database with its schema
psql -h <partner-db-ip> -U partner_user -d partner_management -f sql/partner_management_init.sql
psql -h <onboarding-db-ip> -U onboarding_user -d onboarding -f sql/onboarding_init.sql
psql -h <recruitment-db-ip> -U recruitment_user -d recruitment -f sql/recruitment_init.sql
psql -h <campaign-db-ip> -U campaign_user -d campaign_management -f sql/campaign_management_init.sql
```

### **Step 4: Deploy Updated Services**

```bash
# Deploy with separate databases
kubectl apply -k k8s/database-separation/

# Verify deployment
kubectl get all -n hexabuilders
```

## �� Development Environment

### **Using Separate Databases Locally**

```bash
# Start with separate databases
docker-compose -f docker-compose.separated-databases.yml up -d

# Services will be available on:
# - Partner Management: http://localhost:5000
# - Onboarding: http://localhost:5001
# - Recruitment: http://localhost:5002
# - Campaign Management: http://localhost:5003
```

### **Database Ports**
- Partner Management: `localhost:5433`
- Onboarding: `localhost:5434`
- Recruitment: `localhost:5435`
- Campaign Management: `localhost:5436`

## 📊 Database Configuration

### **Connection Strings**

#### **Partner Management**
```
postgresql://partner_user:partner_secure_password@partner-db-instance:5432/partner_management
```

#### **Onboarding**
```
postgresql://onboarding_user:onboarding_secure_password@onboarding-db-instance:5432/onboarding
```

#### **Recruitment**
```
postgresql://recruitment_user:recruitment_secure_password@recruitment-db-instance:5432/recruitment
```

#### **Campaign Management**
```
postgresql://campaign_user:campaign_secure_password@campaign-db-instance:5432/campaign_management
```

## 🔒 Security Benefits

### **1. Isolation**
- **Independent access controls** per service
- **Isolated failure domains** - one service DB failure doesn't affect others
- **Service-specific backup** and recovery strategies

### **2. Compliance**
- **Data residency** requirements per service
- **Service-specific encryption** and security policies
- **Audit trails** per service database

### **3. Access Control**
- **Database-level permissions** instead of schema-level
- **Service-specific users** with minimal privileges
- **Network isolation** between services

## 📈 Performance Benefits

### **1. Independent Scaling**
- **Service-specific resource allocation**
- **Different performance tiers** per service
- **Optimized configurations** per workload

### **2. Maintenance**
- **Independent schema evolution** per service
- **Service-specific maintenance windows**
- **Isolated testing** and deployment

### **3. Monitoring**
- **Service-specific metrics** and alerts
- **Independent performance tuning**
- **Isolated troubleshooting**

## ⚠️ Migration Considerations

### **1. Data Migration**
- **Zero-downtime migration** strategy
- **Data consistency** validation
- **Rollback procedures** if needed

### **2. Service Dependencies**
- **Profile 360° API** needs to aggregate from all services
- **Integration events** continue to work across services
- **Cross-service queries** may need optimization

### **3. Monitoring Updates**
- **Database metrics** per service
- **Connection pool** monitoring
- **Performance alerts** per database

## 🧪 Testing Strategy

### **1. Unit Tests**
- **Service-specific database** tests
- **Connection string** validation
- **Schema migration** tests

### **2. Integration Tests**
- **Cross-service communication** validation
- **Profile 360° aggregation** testing
- **Event publishing** verification

### **3. Performance Tests**
- **Database isolation** performance impact
- **Connection pool** efficiency
- **Query performance** per service

## 📋 Rollback Plan

### **If Issues Arise**
1. **Revert to schema separation** temporarily
2. **Update service configurations** to use shared database
3. **Restore from backup** if data corruption
4. **Investigate and fix** issues before retry

### **Rollback Commands**
```bash
# Revert to original deployment
kubectl apply -k k8s/

# Restore shared database
kubectl delete -f k8s/database-separation/
```

## ✅ Success Criteria

### **1. Functional Requirements**
- [ ] All services start successfully with separate databases
- [ ] Profile 360° API aggregates data correctly
- [ ] Integration events work across services
- [ ] Health checks pass for all services

### **2. Performance Requirements**
- [ ] Response times within acceptable limits
- [ ] Database connections stable
- [ ] No memory leaks or resource issues

### **3. Security Requirements**
- [ ] Service isolation maintained
- [ ] Access controls properly configured
- [ ] Audit trails working correctly

## 🎯 Next Steps

1. **Review and approve** this implementation plan
2. **Create GCP database instances** using the provided script
3. **Test in staging environment** with separate databases
4. **Update monitoring** and alerting configurations
5. **Deploy to production** with proper rollback procedures
6. **Monitor performance** and adjust as needed

---

**Note**: This implementation provides proper microservices database isolation while maintaining all existing functionality and improving security, performance, and maintainability.
