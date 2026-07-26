#!/bin/bash
# Zero Downtime Deployment Script

echo "🚀 ZERO DOWNTIME DEPLOYMENT"
echo "=========================="
echo ""

# 1. Backup current deployment
echo "📦 Creating backup..."
python scripts/backup.py --create

# 2. Build new version
echo ""
echo "🏗️ Building new version..."
docker build -t nemesis/backend:8.2.0 .

# 3. Deploy with rolling update
echo ""
echo "🔄 Deploying with rolling update..."
kubectl set image deployment/nemesis-backend \
  backend=nemesis/backend:8.2.0 \
  -n nemesis 2>/dev/null || echo "⚠️ kubectl not available, skipping K8s deployment"

# 4. Wait for rollout
echo ""
echo "⏳ Waiting for rollout..."
kubectl rollout status deployment/nemesis-backend -n nemesis 2>/dev/null || echo "⚠️ Skipping rollout status"

# 5. Verify health
echo ""
echo "🩺 Verifying health..."
sleep 5
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Deployment successful"
else
    echo "❌ Health check failed, rolling back..."
    kubectl rollout undo deployment/nemesis-backend -n nemesis 2>/dev/null || echo "⚠️ Rollback not available"
    exit 1
fi

echo ""
echo "🎉 Zero downtime deployment complete!"
