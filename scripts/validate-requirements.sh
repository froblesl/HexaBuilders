#!/bin/bash

# Script to validate that all deployment files are using the correct requirements files
# Usage: ./validate-requirements.sh

set -e

echo "🔍 Validating Requirements Files in Deployment Configurations..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 missing${NC}"
        return 1
    fi
}

# Function to check if Dockerfile uses correct requirements
check_dockerfile_requirements() {
    local dockerfile="$1"
    local expected_req1="$2"
    local expected_req2="$3"
    
    echo "Checking $dockerfile..."
    
    if [ ! -f "$dockerfile" ]; then
        echo -e "${RED}❌ $dockerfile not found${NC}"
        return 1
    fi
    
    # Check if it copies the requirements files
    if grep -q "COPY $expected_req1" "$dockerfile"; then
        echo -e "${GREEN}✅ $dockerfile copies $expected_req1${NC}"
    else
        echo -e "${RED}❌ $dockerfile missing COPY $expected_req1${NC}"
    fi
    
    if [ -n "$expected_req2" ]; then
        if grep -q "COPY $expected_req2" "$dockerfile"; then
            echo -e "${GREEN}✅ $dockerfile copies $expected_req2${NC}"
        else
            echo -e "${RED}❌ $dockerfile missing COPY $expected_req2${NC}"
        fi
    fi
    
    # Check if it installs the requirements
    if grep -q "pip install.*$expected_req1" "$dockerfile"; then
        echo -e "${GREEN}✅ $dockerfile installs $expected_req1${NC}"
    else
        echo -e "${RED}❌ $dockerfile missing pip install $expected_req1${NC}"
    fi
    
    if [ -n "$expected_req2" ]; then
        if grep -q "pip install.*$expected_req2" "$dockerfile"; then
            echo -e "${GREEN}✅ $dockerfile installs $expected_req2${NC}"
        else
            echo -e "${RED}❌ $dockerfile missing pip install $expected_req2${NC}"
        fi
    fi
    
    echo ""
}

echo "📋 Checking Requirements Files..."
check_file "requirements.txt"
check_file "requirements-bff.txt"
check_file "pulsar-requirements.txt"
echo ""

echo "🐳 Checking Dockerfiles..."

# Microservices (should use requirements.txt + pulsar-requirements.txt)
check_dockerfile_requirements "src/partner_management/Dockerfile" "requirements.txt" "pulsar-requirements.txt"
check_dockerfile_requirements "src/onboarding/Dockerfile" "requirements.txt" "pulsar-requirements.txt"
check_dockerfile_requirements "src/recruitment/Dockerfile" "requirements.txt" "pulsar-requirements.txt"
check_dockerfile_requirements "src/campaign_management/Dockerfile" "requirements.txt" "pulsar-requirements.txt"

# Notifications (should use requirements.txt + pulsar-requirements.txt)
check_dockerfile_requirements "dockerfiles/notifications.Dockerfile" "requirements.txt" "pulsar-requirements.txt"

# BFF Web (should use only requirements-bff.txt)
check_dockerfile_requirements "dockerfiles/bff_web.Dockerfile" "requirements-bff.txt" ""

echo "🐙 Checking Docker Compose Files..."

# Check if all services are included in production compose
echo "Checking docker-compose.production.yml..."

services=("partner-management" "onboarding" "recruitment" "campaign-management" "notifications" "bff-web")
for service in "${services[@]}"; do
    if grep -q "$service:" docker-compose.production.yml; then
        echo -e "${GREEN}✅ $service included in production compose${NC}"
    else
        echo -e "${RED}❌ $service missing from production compose${NC}"
    fi
done

echo ""
echo "📊 Requirements Summary:"
echo "========================"

echo "Microservices (partner-management, onboarding, recruitment, campaign-management):"
echo "  - requirements.txt (Flask, SQLAlchemy, psycopg2, etc.)"
echo "  - pulsar-requirements.txt (pulsar-client, fastavro, avro-python3)"

echo ""
echo "Notifications Service:"
echo "  - requirements.txt (Flask, Flask-CORS)"
echo "  - pulsar-requirements.txt (for future Pulsar integration)"

echo ""
echo "BFF Web Service:"
echo "  - requirements-bff.txt (FastAPI, Strawberry GraphQL, httpx, etc.)"

echo ""
echo "🔍 Checking for potential issues..."

# Check for duplicate dependencies
echo "Checking for duplicate dependencies in requirements-bff.txt..."
if grep -c "httpx" requirements-bff.txt | grep -q "2"; then
    echo -e "${YELLOW}⚠️  Duplicate httpx entry found in requirements-bff.txt${NC}"
else
    echo -e "${GREEN}✅ No duplicate httpx entries${NC}"
fi

# Check for version conflicts
echo "Checking for version conflicts..."
if grep -q "pydantic==2.5.0" requirements-bff.txt && grep -q "pydantic==2.10.0" requirements.txt; then
    echo -e "${YELLOW}⚠️  Pydantic version mismatch: BFF uses 2.5.0, microservices use 2.10.0${NC}"
else
    echo -e "${GREEN}✅ No version conflicts detected${NC}"
fi

echo ""
echo "✅ Requirements validation complete!"
