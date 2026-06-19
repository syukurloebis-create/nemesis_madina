#!/bin/bash
# ============================================
# NEMESIS PHASE 0 ORCHESTRATOR
# Menjalankan semua langkah fase 0 secara berurutan
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# KONFIGURASI - SESUAIKAN DENGAN PATH ANDA!
PROJECT_ROOT="/c/Users/LENOVO/nemesis_madina"  # <-- PATH YANG DIPERBAIKI

# Buat direktori jika belum ada
mkdir -p "${PROJECT_ROOT}" 2>/dev/null || true

# Cek apakah project root ada
if [ ! -d "${PROJECT_ROOT}" ]; then
    echo -e "${RED}✗ Project root not found: ${PROJECT_ROOT}${NC}"
    echo -e "${YELLOW}Please update PROJECT_ROOT variable in this script${NC}"
    exit 1
fi

cd "${PROJECT_ROOT}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NEMESIS PHASE 0 - PREPARATION${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Start time: $(date)"
echo -e "Project: ${PROJECT_ROOT}\n"

# Create reports directory
mkdir -p reports/fase0
mkdir -p scripts/fase0

# Step 1: Backup
echo -e "\n${YELLOW}[STEP 1/7] Creating backup...${NC}"
if bash scripts/fase0/01_backup.sh; then
    echo -e "${GREEN}✓ Backup completed${NC}"
else
    echo -e "${RED}✗ Backup failed! Aborting.${NC}"
    exit 1
fi

# Step 2: Detect dead code
echo -e "\n${YELLOW}[STEP 2/7] Detecting dead code...${NC}"
if python scripts/fase0/02_detect_dead_code.py; then
    echo -e "${GREEN}✓ Dead code detection completed${NC}"
else
    echo -e "${YELLOW}⚠ Dead code detected (non-fatal)${NC}"
fi

# Step 3: Cleanup (interactive)
echo -e "\n${YELLOW}[STEP 3/7] Dead code cleanup...${NC}"
echo -e "${RED}This step will DELETE files. Make sure backup exists!${NC}"
read -p "Run cleanup? (y/n): " RUN_CLEANUP
if [ "$RUN_CLEANUP" = "y" ]; then
    if bash scripts/fase0/03_cleanup_dead_code.sh; then
        echo -e "${GREEN}✓ Cleanup completed${NC}"
    else
        echo -e "${RED}✗ Cleanup failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipped cleanup${NC}"
fi

# Step 4: Baseline snapshot
echo -e "\n${YELLOW}[STEP 4/7] Collecting baseline metrics...${NC}"
if python scripts/fase0/04_baseline_snapshot.py; then
    echo -e "${GREEN}✓ Baseline snapshot completed${NC}"
else
    echo -e "${RED}✗ Baseline snapshot failed${NC}"
fi

# Step 5: Import guard
echo -e "\n${YELLOW}[STEP 5/7] Running import guard...${NC}"
if python scripts/fase0/05_import_guard.py; then
    echo -e "${GREEN}✓ Import guard passed${NC}"
else
    echo -e "${RED}✗ Import guard failed! Fix issues before Phase 1.${NC}"
fi

# Step 6: Generate rollback
echo -e "\n${YELLOW}[STEP 6/7] Generating rollback script...${NC}"
if python scripts/fase0/06_generate_rollback.py; then
    echo -e "${GREEN}✓ Rollback script generated${NC}"
else
    echo -e "${RED}✗ Rollback generation failed${NC}"
fi

# Step 7: Validate environment
echo -e "\n${YELLOW}[STEP 7/7] Validating environment...${NC}"
if python scripts/fase0/07_validate_environment.py; then
    echo -e "${GREEN}✓ Environment validation passed${NC}"
else
    echo -e "${RED}✗ Environment validation failed${NC}"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}PHASE 0 COMPLETED${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "End time: $(date)"
echo -e "\nReports saved to: reports/fase0/"
echo -e "\n${GREEN}Next: Proceed to Phase 1 - Canonical Consolidation${NC}"
echo -e "${YELLOW}Before Phase 1, review:${NC}"
echo -e "  - reports/fase0/dead_code_report.json"
echo -e "  - reports/fase0/import_guard_report.json"
echo -e "  - reports/fase0/baseline_latest.json"