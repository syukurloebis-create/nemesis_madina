#!/bin/bash
# ============================================================================
# NEMESIS FASE 5 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 5 - OBSERVABILITY & MONITORING        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 4 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase4" ]; then
    log_error "Fase 4 not completed. Please run Fase 4 first."
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="C:/Users/LENOVO/nemesis_madina"

# Step 1: Create telemetry core
log_info "[1/2] Creating telemetry core..."
python "$SCRIPT_DIR/01_create_telemetry_core.py"
if [ $? -ne 0 ]; then
    log_error "Telemetry core creation failed"
    exit 1
fi

# Step 2: Create exporters
log_info "[2/2] Creating exporters..."
python "$SCRIPT_DIR/02_create_exporters.py"
if [ $? -ne 0 ]; then
    log_error "Exporters creation failed"
    exit 1
fi

# Validation
log_info "Running validation..."
python "$SCRIPT_DIR/03_validate_fase5.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase5" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": [
    "metrics",
    "logging",
    "tracing",
    "dashboard",
    "alerts",
    "health",
    "prometheus_exporter",
    "file_exporter",
    "grafana_exporter"
  ]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 5 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Metrics: Prometheus-style counters, gauges, histograms"
log_success "Logging: Structured JSON logging with trace context"
log_success "Tracing: Distributed tracing support"
log_success "Dashboard: Metrics dashboard API"
log_success "Alerts: Alerting rules and notifications"
log_success "Health: Enhanced health checks for k8s"
log_success "Exporters: Prometheus, File, Grafana formats"
log_info "Next: Fase 6 - Testing Matrix"

exit 0