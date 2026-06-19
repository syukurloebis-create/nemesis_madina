#!/bin/bash

# NEMESIS V8+ Deployment Script
echo "========================================="
echo "🚀 NEMESIS V8+ Deployment"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
echo ""
echo "1️⃣ Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
echo ""
echo "2️⃣ Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Build frontend
echo ""
echo "3️⃣ Building frontend..."
cd frontend
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi
cd ..

# Build backend images
echo ""
echo "4️⃣ Building backend images..."
docker-compose -f docker-compose.lb.yml build --no-cache
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend images built successfully${NC}"
else
    echo -e "${RED}❌ Backend build failed${NC}"
    exit 1
fi

# Start services
echo ""
echo "5️⃣ Starting services..."
docker-compose -f docker-compose.lb.yml up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

# Wait for services to be ready
echo ""
echo "6️⃣ Waiting for services to be ready..."
sleep 30

# Check health
echo ""
echo "7️⃣ Checking health..."
HEALTH=$(curl -s http://localhost/health | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠️ API health check failed${NC}"
fi

# Check frontend
echo ""
echo "8️⃣ Checking frontend..."
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
if [ "$FRONTEND" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠️ Frontend not responding${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}🎉 NEMESIS V8+ Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "🔗 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📋 Login: admin / admin123"
echo "========================================="
