#!/bin/bash
# ============================================================================
# NEMESIS FASE 2 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 2 - DOMAIN RESTRUCTURING              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 1 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase1" ]; then
    log_error "Fase 1 not completed. Please run Fase 1 first."
    exit 1
fi

# Step 1: Create API layer
log_info "[1/4] Creating API layer..."
python "$SCRIPT_DIR/01_create_api_layer.py"
if [ $? -ne 0 ]; then
    log_error "API layer creation failed"
    exit 1
fi

# Step 2: Restructure core
log_info "[2/4] Restructuring core layer..."
python "$SCRIPT_DIR/02_restructure_core.py"
if [ $? -ne 0 ]; then
    log_error "Core restructure failed"
    exit 1
fi

# Step 3: Restructure intelligence
log_info "[3/4] Restructuring intelligence layer..."
python "$SCRIPT_DIR/03_restructure_intelligence.py"
if [ $? -ne 0 ]; then
    log_error "Intelligence restructure failed"
    exit 1
fi

# Step 4: Update main app
log_info "[4/4] Updating main application..."
bash "$SCRIPT_DIR/04_update_main_app.sh"
if [ $? -ne 0 ]; then
    log_error "Main app update failed"
    exit 1
fi

# Step 5: Validation
log_info "Running validation..."
python "$SCRIPT_DIR/05_validate_restructure.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase2" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "layers": ["api", "core", "intelligence"]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 2 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "API layer created with versioning"
log_success "Core layer restructured (entities, services, ports)"
log_success "Intelligence layer reorganized (ml, legal, explainability)"
log_success "Main application updated"
log_info "Next: Fase 3 - Data & Lineage Hardening"

exit 0