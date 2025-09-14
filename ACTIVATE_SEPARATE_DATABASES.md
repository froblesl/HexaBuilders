# How to Activate Separate Databases for Each Service

## 🎯 Current Status

✅ **Services are already configured** to read from `DATABASE_URL` environment variable
✅ **Kubernetes deployments are ready** with separate database secrets  
✅ **Docker Compose is configured** for separate databases in development
✅ **Database schemas are created** for each service

## 🚀 Activation Steps

### **Option 1: Development Environment (Docker Compose)**

```bash
# Stop current services if running
docker-compose down

# Start with separate databases
docker-compose -f docker-compose.separated-databases.yml up -d

# Verify services are using separate databases
curl http://localhost:5000/health  # Partner Management
curl http://localhost:5001/health  # Onboarding  
curl http://localhost:5002/health  # Recruitment
curl http://localhost:5003/health  # Campaign Management
```

**Database Access:**
- Partner Management DB: `localhost:5433`
- Onboarding DB: `localhost:5434` 
- Recruitment DB: `localhost:5435`
- Campaign Management DB: `localhost:5436`

### **Option 2: Production Environment (Kubernetes)**

#### **Step 1: Create GCP Database Instances**
```bash
# Run the database creation script
./scripts/create-separate-databases-gcp.sh YOUR_PROJECT_ID us-central1
```

#### **Step 2: Update Database Secrets with Real Connection Strings**
```bash
# Get the actual database IPs from GCP
PARTNER_DB_IP=$(gcloud sql instances describe partner-db-instance --format="get(ipAddresses[0].ipAddress)")
ONBOARDING_DB_IP=$(gcloud sql instances describe onboarding-db-instance --format="get(ipAddresses[0].ipAddress)")
RECRUITMENT_DB_IP=$(gcloud sql instances describe recruitment-db-instance --format="get(ipAddresses[0].ipAddress)")
CAMPAIGN_DB_IP=$(gcloud sql instances describe campaign-db-instance --format="get(ipAddresses[0].ipAddress)")

# Update secrets with real connection strings (base64 encoded)
kubectl patch secret partner-db-secret -n hexabuilders --type='json' -p='[{"op": "replace", "path": "/data/DATABASE_URL", "value": "'$(echo -n "postgresql://partner_user:partner_secure_password@${PARTNER_DB_IP}:5432/partner_management" | base64)'"}]'

kubectl patch secret onboarding-db-secret -n hexabuilders --type='json' -p='[{"op": "replace", "path": "/data/DATABASE_URL", "value": "'$(echo -n "postgresql://onboarding_user:onboarding_secure_password@${ONBOARDING_DB_IP}:5432/onboarding" | base64)'"}]'

kubectl patch secret recruitment-db-secret -n hexabuilders --type='json' -p='[{"op": "replace", "path": "/data/DATABASE_URL", "value": "'$(echo -n "postgresql://recruitment_user:recruitment_secure_password@${RECRUITMENT_DB_IP}:5432/recruitment" | base64)'"}]'

kubectl patch secret campaign-db-secret -n hexabuilders --type='json' -p='[{"op": "replace", "path": "/data/DATABASE_URL", "value": "'$(echo -n "postgresql://campaign_user:campaign_secure_password@${CAMPAIGN_DB_IP}:5432/campaign_management" | base64)'"}]'
```

#### **Step 3: Initialize Databases**
```bash
# Initialize each database with its schema
psql -h $PARTNER_DB_IP -U partner_user -d partner_management -f sql/partner_management_init.sql
psql -h $ONBOARDING_DB_IP -U onboarding_user -d onboarding -f sql/onboarding_init.sql  
psql -h $RECRUITMENT_DB_IP -U recruitment_user -d recruitment -f sql/recruitment_init.sql
psql -h $CAMPAIGN_DB_IP -U campaign_user -d campaign_management -f sql/campaign_management_init.sql
```

#### **Step 4: Deploy Services with Separate Databases**
```bash
# Deploy using the database-separation configuration
kubectl apply -k k8s/database-separation/

# Verify all pods are running
kubectl get pods -n hexabuilders

# Check services
kubectl get services -n hexabuilders
```

## 🔍 Verification Steps

### **1. Check Database Connections**
```bash
# Test database connectivity from each pod
kubectl exec -it $(kubectl get pods -n hexabuilders -l app=partner-management -o jsonpath='{.items[0].metadata.name}') -n hexabuilders -- python3 -c "
import os, psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✅ Partner Management DB: Connected')
    conn.close()
except Exception as e:
    print(f'❌ Partner Management DB: {e}')
"

kubectl exec -it $(kubectl get pods -n hexabuilders -l app=onboarding -o jsonpath='{.items[0].metadata.name}') -n hexabuilders -- python3 -c "
import os, psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✅ Onboarding DB: Connected')
    conn.close()
except Exception as e:
    print(f'❌ Onboarding DB: {e}')
"

# Similar checks for recruitment and campaign-management...
```

### **2. Verify Service Health**
```bash
# Get service endpoints
kubectl get services -n hexabuilders

# Test health endpoints
curl http://<partner-management-ip>:5000/health
curl http://<onboarding-ip>:5001/health
curl http://<recruitment-ip>:5002/health
curl http://<campaign-management-ip>:5003/health
```

### **3. Test Cross-Service Communication**
```bash
# Test Profile 360° API (should aggregate from all services)
curl http://<partner-management-ip>:5000/api/v1/partners-query/<partner-id>/profile-360
```

## 🔧 Troubleshooting

### **Database Connection Issues**
```bash
# Check secrets are properly configured
kubectl get secret partner-db-secret -n hexabuilders -o yaml
kubectl get secret onboarding-db-secret -n hexabuilders -o yaml

# Check environment variables in pods
kubectl exec -it <pod-name> -n hexabuilders -- env | grep DATABASE_URL
```

### **Service Startup Issues**
```bash
# Check pod logs
kubectl logs -f <pod-name> -n hexabuilders

# Check pod events
kubectl describe pod <pod-name> -n hexabuilders
```

### **Network Connectivity Issues**
```bash
# Test database connectivity from within cluster
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql postgresql://partner_user:partner_secure_password@partner-db-instance:5432/partner_management
```

## ✅ Success Indicators

When everything is working correctly, you should see:

1. **All pods running**: `kubectl get pods -n hexabuilders`
2. **Health checks passing**: All `/health` endpoints return 200
3. **Database isolation**: Each service connects to its own database
4. **Cross-service communication**: Profile 360° API works
5. **No shared database dependencies**: Each service is independent

## 🔄 Rollback Plan

If issues occur:
```bash
# Revert to shared database
kubectl delete -k k8s/database-separation/
kubectl apply -k k8s/

# This restores the shared PostgreSQL configuration
```

---

**The services are already configured to use separate databases - you just need to deploy the right configuration!**
