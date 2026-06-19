#!/bin/bash

# Script untuk inisialisasi dashboard Nemesis V8+

echo "🚀 Initializing Nemesis V8+ Dashboards..."

# Create directories
mkdir -p grafana/dashboards
mkdir -p grafana/provisioning/{datasources,dashboards}
mkdir -p prometheus

# Check if docker-compose is running
if ! docker-compose -f docker-compose.lb.yml ps | grep -q "grafana"; then
    echo "Starting services..."
    docker-compose -f docker-compose.lb.yml up -d
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if dashboards are loaded
echo "Checking Grafana API..."
curl -s -u admin:admin http://localhost:3000/api/health

echo ""
echo "✅ Nemesis V8+ Dashboards initialized!"
echo ""
echo "📊 Access Dashboard:"
echo "   Executive:   http://localhost:3000/d/nemesis-v8-exec"
echo "   Analytics:   http://localhost:3000/d/nemesis-v8-analytics"
echo "   Audit:       http://localhost:3000/d/nemesis-v8-audit"
echo ""
echo "🔐 Login: admin / admin"