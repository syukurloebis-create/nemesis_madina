#!/usr/bin/env python3
"""
NEMESIS FASE 7 - Create Deployment Scripts
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_build_script():
    """Create build.sh script"""
    print("\n[1/4] Creating build.sh...")
    
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Build Script
# ============================================================================

set -e

echo "Building NEMESIS..."

# Set variables
IMAGE_NAME="nemesis"
VERSION=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-}

# Build Docker image
echo "Building Docker image..."
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${VERSION}"
else
    FULL_IMAGE="${IMAGE_NAME}:${VERSION}"
fi

docker build -t ${FULL_IMAGE} -f Dockerfile .

# Tag as latest if version specified
if [ "$VERSION" != "latest" ]; then
    docker tag ${FULL_IMAGE} ${IMAGE_NAME}:latest
fi

echo "Build complete: ${FULL_IMAGE}"

# Push if registry specified
if [ -n "$REGISTRY" ] && [ "$PUSH" = "true" ]; then
    echo "Pushing to registry..."
    docker push ${FULL_IMAGE}
    if [ "$VERSION" != "latest" ]; then
        docker push ${IMAGE_NAME}:latest
    fi
    echo "Push complete"
fi
'''
    
    file_path = PROJECT_ROOT / "scripts" / "build.sh"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_deploy_script():
    """Create deploy.sh script"""
    print("\n[2/4] Creating deploy.sh...")
    
    content = '''#!/bin/bash
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
'''
    
    file_path = PROJECT_ROOT / "scripts" / "deploy.sh"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_healthcheck_script():
    """Create healthcheck.sh script"""
    print("\n[3/4] Creating healthcheck.sh...")
    
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Health Check Script
# ============================================================================

API_URL=${API_URL:-http://localhost:8000}
WS_URL=${WS_URL:-ws://localhost:8001}

echo "Running health checks..."

# API Health
echo -n "API Health: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# API Readiness
echo -n "API Readiness: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health/ready)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# Metrics endpoint
echo -n "Metrics endpoint: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/metrics)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# WebSocket (simple check)
echo -n "WebSocket: "
if command -v wscat &> /dev/null; then
    echo "WebSocket check requires wscat"
else
    echo "Skipped (install wscat for WebSocket tests)"
fi

echo "All health checks passed!"
'''
    
    file_path = PROJECT_ROOT / "scripts" / "healthcheck.sh"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_rollback_script():
    """Create rollback.sh script"""
    print("\n[4/4] Creating rollback.sh...")
    
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Rollback Script
# ============================================================================

set -e

NAMESPACE=${NAMESPACE:-nemesis}
REVISION=${1:-1}

echo "Rolling back NEMESIS to revision ${REVISION}..."

# Rollback API
echo "Rolling back API..."
kubectl rollout undo deployment/nemesis-api -n ${NAMESPACE} --to-revision=${REVISION}

# Rollback WebSocket
echo "Rolling back WebSocket..."
kubectl rollout undo deployment/nemesis-websocket -n ${NAMESPACE} --to-revision=${REVISION}

# Rollback Worker
echo "Rolling back Worker..."
kubectl rollout undo deployment/nemesis-worker -n ${NAMESPACE} --to-revision=${REVISION}

# Wait for rollback
echo "Waiting for rollback to complete..."
kubectl rollout status deployment/nemesis-api -n ${NAMESPACE} --timeout=5m
kubectl rollout status deployment/nemesis-websocket -n ${NAMESPACE} --timeout=5m
kubectl rollout status deployment/nemesis-worker -n ${NAMESPACE} --timeout=5m

echo "Rollback completed!"

# Verify rollback
echo "Verifying rollback..."
if curl -f http://localhost:8000/health; then
    echo "Rollback verification passed!"
else
    echo "Rollback verification failed!"
    exit 1
fi
'''
    
    file_path = PROJECT_ROOT / "scripts" / "rollback.sh"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 7: CREATE DEPLOYMENT SCRIPTS")
    print("="*60)
    
    create_build_script()
    create_deploy_script()
    create_healthcheck_script()
    create_rollback_script()
    
    # Make scripts executable
    for script in ["build.sh", "deploy.sh", "healthcheck.sh", "rollback.sh"]:
        path = PROJECT_ROOT / "scripts" / script
        path.chmod(0o755)
    
    print("\n" + "="*60)
    print("[OK] Deployment scripts created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())