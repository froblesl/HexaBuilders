#!/bin/bash

# Test Database Connections Script
echo "🔍 Testing Database Connections..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Docker Compose database connections (if running)
if docker-compose -f docker-compose.separated-databases.yml ps 2>/dev/null | grep -q "Up"; then
    echo -e "${YELLOW}Testing Docker Compose database connections...${NC}"
    
    # Test service health endpoints
    for port in 5000 5001 5002 5003; do
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service on port $port: Health check passed${NC}"
        else
            echo -e "${RED}❌ Service on port $port: Health check failed${NC}"
        fi
    done
else
    echo -e "${YELLOW}Docker Compose services not running. Start with:${NC}"
    echo "docker-compose -f docker-compose.separated-databases.yml up -d"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ Database connection testing complete!${NC}"
