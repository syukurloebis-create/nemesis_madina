#!/bin/bash
# ============================================================================
# NEMESIS Deploy Script
# ============================================================================

set -e

NAMESPACE=${NAMESPACE:-nemesis}
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "Deploying NEMESIS to ${ENVIRONMENT}..."

# Apply namespace
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets (if exists)
if [ -f "k8s/secret-${ENVIRONMENT}.yaml" ]; then
    kubectl apply -f k8s/secret-${ENVIRONMENT}.yaml -n ${NAMESPACE}
fi

# Apply configmap
kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE}

# Update deployment images
kubectl set image deployment/nemesis-api api=${IMAGE_NAME}:${VERSION} -n ${NAMESPACE} --record
kubectl set image deployment/nemesis-websocket websocket=${IMAGE_NAME}:${VERSION} -n ${NAMESPACE} --record
kubectl set image deployment/nemesis-worker worker=${IMAGE_NAME}:${VERSION} -n ${NAMESPACE} --record

# Wait for rollout
echo "Waiting for API rollout..."
kubectl rollout status deployment/nemesis-api -n ${NAMESPACE} --timeout=5m

echo "Waiting for WebSocket rollout..."
kubectl rollout status deployment/nemesis-websocket -n ${NAMESPACE} --timeout=5m

echo "Waiting for Worker rollout..."
kubectl rollout status deployment/nemesis-worker -n ${NAMESPACE} --timeout=5m

# Apply services
kubectl apply -f k8s/service.yaml -n ${NAMESPACE}

# Apply ingress
kubectl apply -f k8s/ingress.yaml -n ${NAMESPACE}

# Health check
echo "Running health check..."
sleep 10
kubectl port-forward service/nemesis-api 8000:80 -n ${NAMESPACE} &
PF_PID=$!
sleep 5

if curl -f http://localhost:8000/health; then
    echo "Health check passed!"
else
    echo "Health check failed!"
    kill $PF_PID
    exit 1
fi

kill $PF_PID
echo "Deployment completed successfully!"
