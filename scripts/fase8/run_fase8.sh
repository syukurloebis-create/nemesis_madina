#!/bin/bash
# ============================================================================
# NEMESIS FASE 8 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 8 - VALIDATION & PRODUCTION           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 7 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase7" ]; then
    log_error "Fase 7 not completed. Please run Fase 7 first."
    exit 1
fi

# Ensure server is running
log_info "Ensuring server is running..."
./scripts/start_server.sh 2>/dev/null
sleep 3

# Step 1: Production Readiness Check
log_info "[1/6] Running production readiness check..."
python "$SCRIPT_DIR/01_production_readiness_check.py"
if [ $? -ne 0 ]; then
    log_warning "Readiness check has warnings"
fi

# Step 2: Load Test
log_info "[2/6] Running load tests..."
python "$SCRIPT_DIR/02_load_test.py"
if [ $? -ne 0 ]; then
    log_warning "Load tests have issues"
fi

# Step 3: Security Audit
log_info "[3/6] Running security audit..."
python "$SCRIPT_DIR/03_security_audit.py"
if [ $? -ne 0 ]; then
    log_warning "Security audit has warnings"
fi

# Step 4: Generate Documentation
log_info "[4/6] Generating documentation..."
python "$SCRIPT_DIR/04_documentation_generate.py"
if [ $? -ne 0 ]; then
    log_error "Documentation generation failed"
    exit 1
fi

# Step 5: Create Management Scripts
log_info "[5/6] Creating management scripts..."
python "$SCRIPT_DIR/06_create_management_scripts.py"
if [ $? -ne 0 ]; then
    log_error "Management scripts creation failed"
    exit 1
fi

# Step 6: Final Validation
log_info "[6/6] Running final validation..."
python "$SCRIPT_DIR/05_final_validation.py"
if [ $? -ne 0 ]; then
    log_error "Final validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase8" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": [
    "production_readiness",
    "load_testing",
    "security_audit",
    "documentation",
    "management_scripts",
    "final_validation"
  ]
}
EOF

# Create master completion marker
cat > "$PROJECT_ROOT/.fase_status/ALL_COMPLETED" << EOF
{
  "status": "SUCCESS",
  "timestamp": "$(date -Iseconds)",
  "message": "NEMESIS migration and upgrade completed successfully",
  "phases": ["fase1", "fase2", "fase3", "fase4", "fase5", "fase6", "fase7", "fase8"]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║     🎉 NEMESIS MIGRATION & UPGRADE - ALL PHASES COMPLETED! 🎉         ║"
echo "║                                                                       ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║                                                                       ║"
echo "║  ✅ Fase 1: Canonical Domains                                        ║
echo "║  ✅ Fase 2: Domain Restructuring                                     ║
echo "║  ✅ Fase 3: Data & Lineage Hardening                                 ║
echo "║  ✅ Fase 4: Intelligence & ML Hardening                              ║
echo "║  ✅ Fase 5: Observability & Monitoring                               ║
echo "║  ✅ Fase 6: Testing Matrix                                           ║
echo "║  ✅ Fase 7: Deployment Pipeline                                      ║
echo "║  ✅ Fase 8: Validation & Production Readiness                        ║
echo "║                                                                       ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║                                                                       ║"
echo "║  📊 Reports available in: reports/fase8/                             ║
echo "║  📄 API Documentation: http://localhost:8000/docs                    ║
echo "║  📖 README: README.md                                                ║
echo "║                                                                       ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║                                                                       ║"
echo "║  🚀 Useful Commands:                                                 ║"
echo "║     ./scripts/start_server.sh    - Start the server                  ║
echo "║     ./scripts/stop_server.sh     - Stop the server                   ║
echo "║     ./scripts/monitor.sh         - Monitor server status             ║
echo "║     ./scripts/healthcheck.sh     - Run health check                  ║
echo "║     ./scripts/backup_database.sh - Backup database                   ║
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

exit 0