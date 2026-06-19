#!/bin/bash
# Deploy NEMESIS MADINA with Load Balancer

set -e

echo "🚀 Deploying NEMESIS MADINA with Load Balancer..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build images
echo -e "${YELLOW}Building images...${NC}"
docker compose -f docker-compose.lb.yml build

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker compose -f docker-compose.lb.yml down 2>/dev/null || true

# Start services
echo -e "${YELLOW}Starting services with load balancer...${NC}"
docker compose -f docker-compose.lb.yml up -d

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

# Health check
echo -e "${YELLOW}Health check...${NC}"
if curl -s http://localhost/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Load balancer is healthy!${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test load balancing
echo -e "\n${YELLOW}Testing load balancing...${NC}"
for i in {1..10}; do
    RESPONSE=$(curl -s -o /dev/null -w "Request $i: Upstream: %{header_x-upstream}\n" http://localhost/health 2>/dev/null)
    echo "$RESPONSE"
done

# Show status
echo -e "\n${GREEN}=== Deployment Status ===${NC}"
docker compose -f docker-compose.lb.yml ps

echo -e "\n${GREEN}=== API Endpoints ===${NC}"
echo "Load Balancer: http://localhost"
echo "Health Check: http://localhost/health"
echo "Metrics: http://localhost/metrics"
echo "API Docs: http://localhost/docs"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Nginx Status: http://localhost:8080/nginx_status"

echo -e "\n${GREEN}🎉 NEMESIS MADINA deployed with load balancer!${NC}"