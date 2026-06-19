#!/usr/bin/env python3
"""
NEMESIS Rollback Script Generator - Phase 0
Membuat script rollback otomatis
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# KONFIGURASI - SESUAIKAN DENGAN PATH ANDA!
PROJECT_ROOT = Path("C:/Users/LENOVO/nemesis_madina")
BACKUP_ROOT = Path("C:/backup/nemesis")

class RollbackGenerator:
    def __init__(self):
        self.latest_backup = None
        
    def find_latest_backup(self) -> Path:
        """Find most recent backup directory"""
        if not BACKUP_ROOT.exists():
            print(f"❌ Backup root not found: {BACKUP_ROOT}")
            return None
            
        backups = sorted([d for d in BACKUP_ROOT.iterdir() if d.is_dir()], reverse=True)
        if not backups:
            print("❌ No backups found")
            return None
            
        self.latest_backup = backups[0]
        print(f"📁 Latest backup: {self.latest_backup}")
        return self.latest_backup
        
    def generate_rollback_script(self, backup_path: Path) -> Path:
        """Generate rollback script - tanpa karakter Unicode bermasalah"""
        script_content = '''#!/bin/bash
# ============================================
# NEMESIS ROLLBACK SCRIPT
# Generated: ''' + datetime.now().isoformat() + '''
# Backup: ''' + str(backup_path) + '''
# ============================================

set -e

RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

PROJECT_ROOT="''' + str(PROJECT_ROOT) + '''"
BACKUP_PATH="''' + str(backup_path) + '''"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${RED}========================================${NC}"
echo -e "${RED}NEMESIS ROLLBACK${NC}"
echo -e "${RED}========================================${NC}"
echo -e "Backup: ${BACKUP_PATH}"
echo -e "Target: ${PROJECT_ROOT}"

if [ ! -d "${PROJECT_ROOT}" ]; then
    echo -e "${RED}Project root not found: ${PROJECT_ROOT}${NC}"
    exit 1
fi

echo -e "\\n${YELLOW}WARNING: This will OVERWRITE current code!${NC}"
echo -e "Press Ctrl+C to cancel, or Enter to continue..."
read

# 1. Stop services (if any)
echo -e "\\n${YELLOW}[1/4] Stopping services...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl stop nemesis-api 2>/dev/null || true
    sudo systemctl stop nemesis-worker 2>/dev/null || true
fi
echo -e "${GREEN}Services stopped${NC}"

# 2. Backup current state before rollback
echo -e "\\n${YELLOW}[2/4] Creating pre-rollback backup...${NC}"
PRE_ROLLBACK_DIR="C:/backup/nemesis/pre_rollback_${TIMESTAMP}"
mkdir -p "${PRE_ROLLBACK_DIR}"
cp -r "${PROJECT_ROOT}" "${PRE_ROLLBACK_DIR}/" 2>/dev/null || true
echo -e "${GREEN}Pre-rollback backup saved to ${PRE_ROLLBACK_DIR}${NC}"

# 3. Restore from backup
echo -e "\\n${YELLOW}[3/4] Restoring from backup...${NC}"

# Restore code
if [ -f "${BACKUP_PATH}/code_backup.tar.gz" ]; then
    rm -rf "${PROJECT_ROOT}"/*
    tar -xzf "${BACKUP_PATH}/code_backup.tar.gz" -C "${PROJECT_ROOT}/"
    echo -e "${GREEN}Code restored${NC}"
else
    echo -e "${RED}Code backup not found!${NC}"
fi

# Restore config files
if [ -d "${BACKUP_PATH}/config" ]; then
    cp -r "${BACKUP_PATH}/config/"* "${PROJECT_ROOT}/" 2>/dev/null || true
    echo -e "${GREEN}Config restored${NC}"
fi

# 4. Restart services
echo -e "\\n${YELLOW}[4/4] Restarting services...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl start nemesis-api 2>/dev/null || true
    sudo systemctl start nemesis-worker 2>/dev/null || true
fi
echo -e "${GREEN}Services restarted${NC}"

# Verification
echo -e "\\n${GREEN}========================================${NC}"
echo -e "${GREEN}ROLLBACK COMPLETED${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\\nVerify the rollback by running:"
echo -e "  python ${PROJECT_ROOT}/scripts/fase0/04_baseline_snapshot.py"
echo -e "\\nIf rollback failed, restore from pre-rollback backup:"
echo -e "  cp -r ${PRE_ROLLBACK_DIR}/* ${PROJECT_ROOT}/"
'''
        rollback_file = PROJECT_ROOT / "scripts" / "rollback.sh"
        rollback_file.parent.mkdir(parents=True, exist_ok=True)
        rollback_file.write_text(script_content, encoding='utf-8')
        rollback_file.chmod(0o755)
        
        print(f"✅ Rollback script created: {rollback_file}")
        return rollback_file
        
    def generate_rollback_manifest(self, backup_path: Path) -> Path:
        """Generate rollback manifest"""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'backup_path': str(backup_path),
            'project_root': str(PROJECT_ROOT),
            'rollback_steps': [
                '1. Stop services (systemctl stop nemesis-*)',
                '2. Create pre-rollback backup',
                '3. Restore code from code_backup.tar.gz',
                '4. Restore config files',
                '5. Restart services',
                '6. Verify with baseline snapshot'
            ],
            'verification_commands': [
                'python scripts/fase0/04_baseline_snapshot.py',
                'python scripts/fase0/05_import_guard.py',
                'pytest tests/ -v --tb=short'
            ]
        }
        
        manifest_file = PROJECT_ROOT / "reports" / "fase0" / "rollback_manifest.json"
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"✅ Rollback manifest created: {manifest_file}")
        return manifest_file
        
    def run(self):
        """Main execution"""
        print("\n" + "="*60)
        print("ROLLBACK SCRIPT GENERATOR")
        print("="*60)
        
        backup = self.find_latest_backup()
        if not backup:
            print("\n❌ No backup found. Please run 01_backup.sh first.")
            return 1
            
        self.generate_rollback_script(backup)
        self.generate_rollback_manifest(backup)
        
        print("\n✅ Rollback preparation completed!")
        print("\nTo test rollback (emergency only):")
        print("  ./scripts/rollback.sh")
        
        return 0

if __name__ == "__main__":
    sys.exit(RollbackGenerator().run())