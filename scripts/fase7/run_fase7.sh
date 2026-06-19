#!/bin/bash
# ============================================================================
# NEMESIS FASE 7 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 7 - DEPLOYMENT PIPELINE               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 6 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase6" ]; then
    log_error "Fase 6 not completed. Please run Fase 6 first."
    exit 1
fi

# Step 1: Create Docker configuration
log_info "[1/4] Creating Docker configuration..."
python "$SCRIPT_DIR/01_create_docker_config.py"
if [ $? -ne 0 ]; then
    log_error "Docker configuration failed"
    exit 1
fi

# Step 2: Create GitHub Actions
log_info "[2/4] Creating GitHub Actions workflows..."
python "$SCRIPT_DIR/02_create_github_actions.py"
if [ $? -ne 0 ]; then
    log_error "GitHub Actions creation failed"
    exit 1
fi

# Step 3: Create Kubernetes manifests
log_info "[3/4] Creating Kubernetes manifests..."
python "$SCRIPT_DIR/03_create_k8s_manifests.py"
if [ $? -ne 0 ]; then
    log_error "Kubernetes manifests creation failed"
    exit 1
fi

# Step 4: Create deployment scripts
log_info "[4/4] Creating deployment scripts..."
python "$SCRIPT_DIR/04_create_deployment_scripts.py"
if [ $? -ne 0 ]; then
    log_error "Deployment scripts creation failed"
    exit 1
fi

# Validation
log_info "Running validation..."
python "$SCRIPT_DIR/05_validate_fase7.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase7" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": [
    "docker_config",
    "github_actions",
    "kubernetes_manifests",
    "deployment_scripts"
  ]
}
EOF

# Make scripts executable
chmod +x "$PROJECT_ROOT/scripts/build.sh"
chmod +x "$PROJECT_ROOT/scripts/deploy.sh"
chmod +x "$PROJECT_ROOT/scripts/healthcheck.sh"
chmod +x "$PROJECT_ROOT/scripts/rollback.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 7 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Docker configuration: Dockerfile, docker-compose.yml"
log_success "GitHub Actions: CI/CD workflows"
log_success "Kubernetes: deployments, services, ingress"
log_success "Deployment scripts: build, deploy, rollback, healthcheck"
echo ""
echo "Quick commands:"
echo "  - Build:     ./scripts/build.sh"
echo "  - Deploy:    ./scripts/deploy.sh staging"
echo "  - Rollback:  ./scripts/rollback.sh 1"
echo "  - Health:    ./scripts/healthcheck.sh"
echo ""

exit 0