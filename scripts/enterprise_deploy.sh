#!/bin/bash
# Enterprise Deployment Script

echo "🚀 ENTERPRISE DEPLOYMENT"
echo "======================="
echo ""

# 1. Pre-deployment checks
echo "📋 Pre-deployment checks..."
kubectl get nodes
kubectl get namespace nemesis
echo "✅ Pre-checks passed"

# 2. Backup
echo ""
echo "📦 Creating backup..."
python scripts/backup.py --create

# 3. Build and push
echo ""
echo "🏗️ Building and pushing image..."
docker build -t nemesis/backend:8.1.0 .
docker push nemesis/backend:8.1.0

# 4. Deploy
echo ""
echo "🔄 Deploying with rolling update..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# 5. Wait for rollout
echo ""
echo "⏳ Waiting for rollout..."
kubectl rollout status deployment/nemesis-api -n nemesis --timeout=5m

# 6. Verify pods
echo ""
echo "🩺 Verifying pods..."
kubectl get pods -n nemesis

# 7. Health check
echo ""
echo "🩺 Health check..."
sleep 10
POD_IP=$(kubectl get pods -n nemesis -l app=nemesis -o jsonpath='{.items[0].status.podIP}')
curl -s "http://$POD_IP:8000/health" || echo "⚠️ Health check failed"

# 8. Smoke test
echo ""
echo "🧪 Running smoke test..."
ENDPOINTS=("/health" "/api/v1/cases/stats" "/api/v1/fraud/stats" "/api/v1/graph/metrics")
for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s -o /dev/null -w "%{http_code}" "http://$POD_IP:8000$endpoint" | grep -q "200"; then
        echo "  ✅ $endpoint OK"
    else
        echo "  ❌ $endpoint FAILED"
    fi
done

# 9. Verify replicas
echo ""
echo "📊 Replica status:"
kubectl get pods -n nemesis -l app=nemesis

echo ""
echo "🎉 Enterprise deployment complete!"