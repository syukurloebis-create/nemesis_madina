#!/bin/bash
# ============================================================================
# NEMESIS FASE 0 - Master Runner
# Menjalankan seluruh fase 0 secara berurutan
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASE0_DIR="${SCRIPT_DIR}/fase0"

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 0 - PREPARATION                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

# Install dependencies
echo -e "${BLUE}[1/7] Installing dependencies...${NC}"
pip install -r "${SCRIPT_DIR}/requirements-fase0.txt" 2>/dev/null || \
    echo -e "${YELLOW}Warning: Could not install all dependencies${NC}"

# Step 1: Backup
echo -e "\n${BLUE}[2/7] Running backup...${NC}"
bash "${FASE0_DIR}/01_backup.sh"
if [ $? -ne 0 ]; then
    echo -e "${RED}Backup failed! Aborting.${NC}"
    exit 1
fi

# Step 2: Detect dead code
echo -e "\n${BLUE}[3/7] Detecting dead code...${NC}"
python "${FASE0_DIR}/02_detect_dead_code.py"

# Step 3: Cleanup (with confirmation)
echo -e "\n${BLUE}[4/7] Running cleanup...${NC}"
bash "${FASE0_DIR}/03_cleanup_dead_code.sh"

# Step 4: Baseline snapshot
echo -e "\n${BLUE}[5/7] Taking baseline snapshot...${NC}"
python "${FASE0_DIR}/04_baseline_snapshot.py"

# Step 5: Import guard
echo -e "\n${BLUE}[6/7] Running import guard...${NC}"
python "${FASE0_DIR}/05_import_guard.py"

# Step 6: Verification
echo -e "\n${BLUE}[7/7] Verifying cleanup...${NC}"
python "${FASE0_DIR}/07_verify_cleanup.py"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 0 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Reports saved in: ${PROJECT_ROOT}/reports/fase0/"
echo "Backup saved in: ../backup_nemesis/"
echo ""
echo "Next: Proceed to Fase 1 - Canonical Consolidation"