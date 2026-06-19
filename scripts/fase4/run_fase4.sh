#!/bin/bash
# ============================================================================
# NEMESIS FASE 4 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 4 - INTELLIGENCE & ML HARDENING       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 3 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase3" ]; then
    log_error "Fase 3 not completed. Please run Fase 3 first."
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="C:/Users/LENOVO/nemesis_madina"

# Step 1: Enhance ML modules
log_info "[1/3] Enhancing ML modules..."
python "$SCRIPT_DIR/01_enhance_ml_modules.py"
if [ $? -ne 0 ]; then
    log_error "ML enhancement failed"
    exit 1
fi

# Step 2: Create explainability modules
log_info "[2/3] Creating explainability modules..."
python "$SCRIPT_DIR/02_create_explainability_modules.py"
if [ $? -ne 0 ]; then
    log_error "Explainability creation failed"
    exit 1
fi

# Step 3: Create ML pipeline
log_info "[3/3] Creating ML pipeline..."
python "$SCRIPT_DIR/03_create_ml_pipeline.py"
if [ $? -ne 0 ]; then
    log_error "ML pipeline creation failed"
    exit 1
fi

# Validation
log_info "Running validation..."
python "$SCRIPT_DIR/04_validate_fase4.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase4" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": [
    "ml_drift_detection",
    "ml_ensemble",
    "ml_feature_store",
    "explainability_lime",
    "explainability_shap",
    "pipeline_trainer",
    "pipeline_predictor",
    "pipeline_validator"
  ]
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 4 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "ML modules: drift detection, ensemble, feature store"
log_success "Explainability: LIME, SHAP, counterfactual explanations"
log_success "ML Pipeline: trainer, batch predictor, validator"
log_info "Next: Fase 5 - Observability & Monitoring"

exit 0