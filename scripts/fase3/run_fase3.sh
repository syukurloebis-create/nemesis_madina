#!/bin/bash
# ============================================================================
# NEMESIS FASE 3 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 3 - DATA & LINEAGE HARDENING          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 2 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase2" ]; then
    log_error "Fase 2 not completed. Please run Fase 2 first."
    exit 1
fi

# Step 1: Enhance evidence hashing
log_info "[1/4] Enhancing evidence hashing..."
python "$SCRIPT_DIR/01_enhance_evidence_hashing.py"
if [ $? -ne 0 ]; then
    log_error "Evidence hashing enhancement failed"
    exit 1
fi

# Step 2: Create lineage tracking
log_info "[2/4] Creating lineage tracking system..."
python "$SCRIPT_DIR/02_create_lineage_tracker.py"
if [ $? -ne 0 ]; then
    log_error "Lineage tracking creation failed"
    exit 1
fi

# Step 3: Create schema registry
log_info "[3/4] Creating schema registry..."
python "$SCRIPT_DIR/03_create_schema_registry.py"
if [ $? -ne 0 ]; then
    log_error "Schema registry creation failed"
    exit 1
fi

# Step 4: Enhance replay engine
log_info "[4/4] Enhancing replay engine..."
python "$SCRIPT_DIR/04_enhance_replay_engine.py"
if [ $? -ne 0 ]; then
    log_error "Replay engine enhancement failed"
    exit 1
fi

# Validation
log_info "Running validation..."
python "$SCRIPT_DIR/05_validate_fase3.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase3" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": ["evidence_hashing", "chain_validator", "lineage_tracker", "schema_registry", "replay_engine"]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 3 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Evidence hashing with chain support"
log_success "Lineage tracking system (tracker, verifier, graph, exporter)"
log_success "Schema registry with versioning"
log_success "Enhanced replay engine with snapshots"
log_info "Next: Fase 4 - Intelligence & ML Hardening"

exit 0