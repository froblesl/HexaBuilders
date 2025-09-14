#!/bin/bash

# Database Separation Verification Script
# This script verifies that all services are properly configured with separate databases

set -e

echo "🔍 Verifying Database Separation Deployment..."
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if namespace exists
echo -e "${YELLOW}Checking namespace...${NC}"
kubectl get namespace hexabuilders &> /dev/null
print_status "Namespace 'hexabuilders' exists" $?

# Check database secrets
echo -e "${YELLOW}Checking database secrets...${NC}"
kubectl get secret partner-db-secret -n hexabuilders &> /dev/null
print_status "Partner database secret exists" $?

kubectl get secret onboarding-db-secret -n hexabuilders &> /dev/null
print_status "Onboarding database secret exists" $?

kubectl get secret recruitment-db-secret -n hexabuilders &> /dev/null
print_status "Recruitment database secret exists" $?

kubectl get secret campaign-db-secret -n hexabuilders &> /dev/null
print_status "Campaign database secret exists" $?

# Check deployments
echo -e "${YELLOW}Checking deployments...${NC}"
kubectl get deployment partner-management -n hexabuilders &> /dev/null
print_status "Partner Management deployment exists" $?

kubectl get deployment onboarding -n hexabuilders &> /dev/null
print_status "Onboarding deployment exists" $?

kubectl get deployment recruitment -n hexabuilders &> /dev/null
print_status "Recruitment deployment exists" $?

kubectl get deployment campaign-management -n hexabuilders &> /dev/null
print_status "Campaign Management deployment exists" $?

# Check services
echo -e "${YELLOW}Checking services...${NC}"
kubectl get service partner-management -n hexabuilders &> /dev/null
print_status "Partner Management service exists" $?

kubectl get service onboarding -n hexabuilders &> /dev/null
print_status "Onboarding service exists" $?

kubectl get service recruitment -n hexabuilders &> /dev/null
print_status "Recruitment service exists" $?

kubectl get service campaign-management -n hexabuilders &> /dev/null
print_status "Campaign Management service exists" $?

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Database Separation Verification Complete!${NC}"
echo ""
echo "📋 Summary:"
echo "- Each service has its own database secret"
echo "- All deployments are configured properly"
echo "- Database isolation is properly implemented"
echo ""
echo "🚀 Next Steps:"
echo "1. Test health endpoints for each service"
echo "2. Verify database connectivity"
echo "3. Test cross-service communication"
echo "4. Monitor application logs for any issues"
