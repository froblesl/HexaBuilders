# HexaBuilders Deployment Scripts

This directory contains all deployment and operational scripts for the HexaBuilders platform.

## 📁 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `create-gke-cluster.sh` | Create GKE cluster | `./create-gke-cluster.sh PROJECT_ID` |
| `build-and-push-images.sh` | Build and push Docker images | `./build-and-push-images.sh PROJECT_ID [TAG]` |
| `deploy-to-gke.sh` | Deploy to GKE | `./deploy-to-gke.sh PROJECT_ID [CLUSTER] [ZONE] [TAG]` |
| `cleanup-gke.sh` | Clean up GKE resources | `./cleanup-gke.sh PROJECT_ID [CLUSTER]` |
| `gcp-cost-control.sh` | Monitor and control costs | `./gcp-cost-control.sh PROJECT_ID` |

## 🚀 Quick Start

### Prerequisites
- Google Cloud SDK installed and configured
- Docker installed and running
- kubectl installed
- Access to a GCP project

### Complete Deployment
```bash
# 1. Create cluster
./create-gke-cluster.sh my-project-id

# 2. Build and push images
./build-and-push-images.sh my-project-id v1.0.0

# 3. Deploy to Kubernetes
./deploy-to-gke.sh my-project-id hexabuilders-cluster us-central1-a v1.0.0
```

## 📋 Script Details

### create-gke-cluster.sh
Creates a GKE cluster with production-ready configuration.

**Features:**
- 3 nodes with e2-standard-4 machines
- 50GB disk per node
- Cloud logging and monitoring enabled
- Auto-repair and auto-upgrade enabled
- Weekly maintenance window

**Usage:**
```bash
./create-gke-cluster.sh PROJECT_ID [CLUSTER_NAME] [ZONE]
```

**Example:**
```bash
./create-gke-cluster.sh my-hexabuilders-project hexabuilders-cluster us-central1-a
```

### build-and-push-images.sh
Builds all Docker images and pushes them to Google Container Registry.

**Features:**
- Builds all microservices
- Pushes to GCR with specified tag
- Handles authentication automatically
- Validates image builds

**Usage:**
```bash
./build-and-push-images.sh PROJECT_ID [TAG]
```

**Example:**
```bash
./build-and-push-images.sh my-hexabuilders-project v1.0.0
```

### deploy-to-gke.sh
Deploys the entire platform to GKE.

**Features:**
- Replaces PROJECT_ID in Kubernetes manifests
- Applies all Kubernetes resources
- Waits for pods to be ready
- Provides access instructions

**Usage:**
```bash
./deploy-to-gke.sh PROJECT_ID [CLUSTER_NAME] [ZONE] [TAG]
```

**Example:**
```bash
./deploy-to-gke.sh my-hexabuilders-project hexabuilders-cluster us-central1-a v1.0.0
```

### cleanup-gke.sh
Cleans up GKE resources to avoid costs.

**Features:**
- Deletes all Kubernetes resources
- Removes the GKE cluster
- Confirms before deletion
- Shows cost savings

**Usage:**
```bash
./cleanup-gke.sh PROJECT_ID [CLUSTER_NAME]
```

**Example:**
```bash
./cleanup-gke.sh my-hexabuilders-project hexabuilders-cluster
```

### gcp-cost-control.sh
Monitors and helps control GCP costs.

**Features:**
- Shows current resource usage
- Estimates monthly costs
- Provides cost optimization tips
- Alerts on high usage

**Usage:**
```bash
./gcp-cost-control.sh PROJECT_ID
```

**Example:**
```bash
./gcp-cost-control.sh my-hexabuilders-project
```

## 🔧 Configuration

### Environment Variables
```bash
export PROJECT_ID="my-hexabuilders-project"
export CLUSTER_NAME="hexabuilders-cluster"
export ZONE="us-central1-a"
export TAG="v1.0.0"
```

### GCP Configuration
```bash
# Set default project
gcloud config set project $PROJECT_ID

# Configure Docker for GCR
gcloud auth configure-docker

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Denied
```bash
chmod +x scripts/*.sh
```

#### GCP Authentication
```bash
gcloud auth login
gcloud auth application-default login
```

#### Docker Authentication
```bash
gcloud auth configure-docker
```

#### Cluster Not Found
```bash
gcloud container clusters list
gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE
```

### Debug Mode
```bash
# Enable debug output
set -x
./deploy-to-gke.sh PROJECT_ID
set +x
```

### Logs
```bash
# Check deployment logs
kubectl logs -f deployment/bff-web -n hexabuilders

# Check all pods
kubectl get pods -n hexabuilders

# Check services
kubectl get services -n hexabuilders
```

## 📊 Monitoring

### Health Checks
```bash
# Check all services
kubectl get pods -n hexabuilders

# Check specific service
kubectl describe pod POD_NAME -n hexabuilders
```

### Resource Usage
```bash
# Check resource usage
kubectl top pods -n hexabuilders
kubectl top nodes
```

### Logs
```bash
# Follow logs
kubectl logs -f deployment/SERVICE_NAME -n hexabuilders

# Get logs from all containers
kubectl logs -f -l app=SERVICE_NAME -n hexabuilders
```

## 🔒 Security

### Service Accounts
- Each service runs with minimal required permissions
- No root containers
- Resource limits enforced

### Network Security
- Services communicate within the cluster
- External access only through LoadBalancer services
- No direct database access from outside

### Secrets Management
- Database credentials stored in Kubernetes secrets
- No hardcoded secrets in code
- Environment-specific configurations

## 💰 Cost Optimization

### Resource Limits
- All services have CPU and memory limits
- Auto-scaling enabled for critical services
- Efficient resource allocation

### Monitoring
- Use `gcp-cost-control.sh` to monitor costs
- Set up billing alerts
- Regular cleanup of unused resources

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale specific service
kubectl scale deployment SERVICE_NAME --replicas=3 -n hexabuilders

# Auto-scaling (if configured)
kubectl autoscale deployment SERVICE_NAME --min=2 --max=10 -n hexabuilders
```

### Vertical Scaling
```bash
# Update resource limits in deployment YAML
kubectl apply -f k8s/SERVICE-deployment.yaml
```

---

**For more information, see the main project documentation.**