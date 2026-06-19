#!/bin/bash
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
