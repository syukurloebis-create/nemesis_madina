#!/bin/bash
# ============================================================================
# NEMESIS FASE 1 - Master Runner
# Menjalankan seluruh fase 1 secara berurutan
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 1 - CANONICALIZATION                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 0 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase0" ]; then
    log_error "Fase 0 not completed. Please run Fase 0 first."
    exit 1
fi

# Step 1: Evidence Canonicalization
log_info "[1/6] Running Evidence Canonicalization..."
python "$SCRIPT_DIR/01_evidence_canonical.py"
if [ $? -ne 0 ]; then
    log_error "Evidence canonicalization failed"
    exit 1
fi

# Step 2: WebSocket Canonicalization
log_info "[2/6] Running WebSocket Canonicalization..."
python "$SCRIPT_DIR/02_websocket_canonical.py"
if [ $? -ne 0 ]; then
    log_error "WebSocket canonicalization failed"
    exit 1
fi

# Step 3: Event Bus Canonicalization
log_info "[3/6] Running Event Bus Canonicalization..."
python "$SCRIPT_DIR/03_eventbus_canonical.py"
if [ $? -ne 0 ]; then
    log_error "Event Bus canonicalization failed"
    exit 1
fi

# Step 4: Graph Canonicalization
log_info "[4/6] Running Graph Canonicalization..."
python "$SCRIPT_DIR/04_graph_canonical.py"
if [ $? -ne 0 ]; then
    log_error "Graph canonicalization failed"
    exit 1
fi

# Step 5: Update Imports (dry run first)
log_info "[5/6] Checking import updates (dry run)..."
python "$SCRIPT_DIR/05_update_imports.py" --dry-run

echo ""
read -p "Apply import changes? (yes/no): " CONFIRM
if [ "$CONFIRM" = "yes" ]; then
    log_info "Applying import updates..."
    python "$SCRIPT_DIR/05_update_imports.py" --apply
else
    log_warning "Skipping import updates"
fi

# Step 6: Verification
log_info "[6/6] Running verification..."
python "$SCRIPT_DIR/06_verify_canonical.py"
if [ $? -ne 0 ]; then
    log_error "Verification failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase1" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "domains": ["evidence", "websocket", "event_bus", "graph"]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 1 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "All canonical domains created"
log_success "Import statements updated"
log_info "Next: Fase 2 - Domain Restructuring"

exit 0