#!/bin/bash
# ============================================
# NEMESIS DEAD CODE CLEANUP - Phase 0
# HAPUS DENGAN HATI-HATI!
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/c/Users/LENOVO/nemesis_madina"  # <-- PATH YANG DIPERBAIKI

if [ ! -d "${PROJECT_ROOT}" ]; then
    echo -e "${RED}✗ Project root not found: ${PROJECT_ROOT}${NC}"
    exit 1
fi

cd "${PROJECT_ROOT}"

echo -e "${RED}========================================${NC}"
echo -e "${RED}⚠️  DEAD CODE CLEANUP${NC}"
echo -e "${RED}========================================${NC}"
echo -e "Project: ${PROJECT_ROOT}"
echo -e "${YELLOW}This will DELETE files marked as dead code.${NC}"
echo -e "${YELLOW}Make sure you have a backup before continuing!${NC}"
echo -e "\nPress Ctrl+C to cancel, or Enter to continue..."
read

# Create backup before cleanup
echo -e "\n${YELLOW}Creating pre-cleanup backup...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/c/backup/nemesis/pre_cleanup_${TIMESTAMP}"
mkdir -p "${BACKUP_DIR}"
cp -r . "${BACKUP_DIR}" 2>/dev/null || true
echo -e "${GREEN}Backup created at: ${BACKUP_DIR}${NC}"

# Count files to be deleted
echo -e "\n${YELLOW}Counting files to delete...${NC}"

# 1. Delete *Salin* files
SALIN_COUNT=$(find . -type f -name "*Salin*" 2>/dev/null | wc -l)
echo -e "  Found ${SALIN_COUNT} *Salin* files"

# 2. Delete *.bak files
BAK_COUNT=$(find . -type f -name "*.bak" 2>/dev/null | wc -l)
echo -e "  Found ${BAK_COUNT} *.bak files"

# 3. Delete *.py.bak
PYBAK_COUNT=$(find . -type f -name "*.py.bak" 2>/dev/null | wc -l)
echo -e "  Found ${PYBAK_COUNT} *.py.bak files"

# 4. Delete *.corrupt
CORRUPT_COUNT=$(find . -type f -name "*.corrupt" 2>/dev/null | wc -l)
echo -e "  Found ${CORRUPT_COUNT} *.corrupt files"

# 5. Count __pycache__
CACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
echo -e "  Found ${CACHE_COUNT} __pycache__ directories"

echo -e "\n${YELLOW}Proceed with deletion? (y/n)${NC}"
read CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo -e "${RED}Cancelled.${NC}"
    exit 0
fi

# Execute deletion
echo -e "\n${GREEN}Executing cleanup...${NC}"

# Delete *Salin* files
find . -type f -name "*Salin*" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *Salin* files"

# Delete *.bak files
find . -type f -name "*.bak" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *.bak files"

# Delete *.py.bak
find . -type f -name "*.py.bak" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *.py.bak files"

# Delete *.corrupt
find . -type f -name "*.corrupt" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *.corrupt files"

# Delete *.old
find . -type f -name "*.old" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *.old files"

# Delete *copy* files (except in node_modules)
find . -type f -name "*copy*" -not -path "*/node_modules/*" -delete 2>/dev/null || true
echo -e "  ✓ Deleted *copy* files"

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "  ✓ Cleaned Python cache"

# Clean .pytest_cache
rm -rf .pytest_cache 2>/dev/null || true
echo -e "  ✓ Removed .pytest_cache"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}CLEANUP COMPLETED${NC}"
echo -e "${GREEN}========================================${NC}"

# Verify cleanup
echo -e "\n${YELLOW}Verifying cleanup...${NC}"
REMAINING=$(find . -type f -name "*Salin*" 2>/dev/null | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}✓ No remaining *Salin* files${NC}"
else
    echo -e "${RED}⚠ ${REMAINING} *Salin* files still exist${NC}"
fi

echo -e "\n${YELLOW}If any issues, restore from backup:${NC}"
echo -e "  cp -r ${BACKUP_DIR}/* ${PROJECT_ROOT}/"