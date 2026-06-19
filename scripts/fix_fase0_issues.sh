#!/bin/bash
# ============================================================================
# NEMESIS FASE 0 - Auto Fix Script
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS FASE 0 - AUTO FIX SCRIPT                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd ~/nemesis_madina

# 1. Fix symlink issue (Windows)
echo -e "${BLUE}[1/5] Fixing symlink issue...${NC}"
rm -f reports/fase0/baseline_latest.json
LATEST=$(ls -t reports/fase0/baseline_*.json 2>/dev/null | head -1)
if [ -f "$LATEST" ]; then
    cp "$LATEST" reports/fase0/baseline_latest.json
    echo -e "${GREEN}  Copied $LATEST to baseline_latest.json${NC}"
else
    echo -e "${YELLOW}  No baseline file found${NC}"
fi

# 2. Delete *Salin* files
echo -e "${BLUE}[2/5] Deleting *Salin* files...${NC}"
SALIN_COUNT=$(find . -name "*Salin*" -type f 2>/dev/null | wc -l)
if [ $SALIN_COUNT -gt 0 ]; then
    find . -name "*Salin*" -type f -delete 2>/dev/null
    echo -e "${GREEN}  Deleted $SALIN_COUNT *Salin* files${NC}"
else
    echo -e "${GREEN}  No *Salin* files found${NC}"
fi

# 3. Delete __pycache__ and .pyc
echo -e "${BLUE}[3/5] Cleaning Python cache...${NC}"
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l)
find . -type f -name "*.pyc" -delete 2>/dev/null
echo -e "${GREEN}  Removed $PYCACHE_COUNT __pycache__ dirs, $PYC_COUNT .pyc files${NC}"

# 4. Fix Python syntax errors
echo -e "${BLUE}[4/5] Fixing Python syntax errors...${NC}"

python -c "
import re
import os

files_to_fix = [
    'backend/routers/trust.py',
    'backend/core/analytics/forensic_engine.py',
    'backend/core/events/lineage_verifier.py'
]

fixed = 0
for f in files_to_fix:
    if not os.path.exists(f):
        print(f'  File not found: {f}')
        continue
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original = content
        
        # Fix empty functions
        content = re.sub(
            r'(def\s+\w+\([^)]*\):\s*\n)(\s*)(?=\n|def|class|@)',
            r'\1\2    pass\n',
            content
        )
        
        # Fix empty with statements
        content = re.sub(
            r'(with\s+.*:\s*\n)(\s*)(?=\n|def|class|@)',
            r'\1\2    pass\n',
            content
        )
        
        # Fix empty try/except
        content = re.sub(
            r'(try:\s*\n)(\s*)(?=\n|except|finally)',
            r'\1\2    pass\n',
            content
        )
        
        if content != original:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f'  Fixed: {f}')
            fixed += 1
        else:
            print(f'  No changes: {f}')
    except Exception as e:
        print(f'  Error fixing {f}: {e}')
"

echo -e "${GREEN}  Fixed $fixed files${NC}"

# 5. Run verification
echo -e "${BLUE}[5/5] Running verification...${NC}"
python scripts/fase0/07_verify_cleanup.py

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 0 AUTO FIX COMPLETE                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""