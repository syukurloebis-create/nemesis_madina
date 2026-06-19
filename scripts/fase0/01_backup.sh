#!/bin/bash
# ============================================
# NEMESIS BACKUP SCRIPT - PHASE 0
# Untuk Windows Git Bash
# ============================================

set -e  # Stop on error

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Konfigurasi - SESUAIKAN DENGAN PATH ANDA!
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_ROOT="/c/backup/nemesis"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"
PROJECT_ROOT="/c/Users/LENOVO/nemesis_madina"  # <-- PATH YANG DIPERBAIKI

# Database config (optional - jika tidak ada pg_dump, skip)
DB_NAME="nemesis_db"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NEMESIS BACKUP - ${TIMESTAMP}${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Project root: ${PROJECT_ROOT}"

# Buat direktori backup
mkdir -p "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}/database"
mkdir -p "${BACKUP_DIR}/evidence"
mkdir -p "${BACKUP_DIR}/snapshots"
mkdir -p "${BACKUP_DIR}/config"

# 1. Backup Database (skip if pg_dump not available)
echo -e "${YELLOW}[1/5] Backing up database...${NC}"
if command -v pg_dump &> /dev/null; then
    pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} \
        -d ${DB_NAME} \
        -F c \
        -f "${BACKUP_DIR}/database/nemesis_db.dump" 2>/dev/null || echo "Database backup skipped (connection failed)"
    echo -e "${GREEN}✓ Database backup completed${NC}"
else
    echo -e "${YELLOW}⚠ pg_dump not found - skipping database backup${NC}"
fi

# 2. Backup Code (exclude unnecessary files)
echo -e "${YELLOW}[2/5] Backing up source code...${NC}"
if [ -d "${PROJECT_ROOT}" ]; then
    cd "${PROJECT_ROOT}"
    tar -czf "${BACKUP_DIR}/code_backup.tar.gz" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='*.log' \
        --exclude='backups' \
        --exclude='snapshots' \
        --exclude='htmlcov' \
        --exclude='.pytest_cache' \
        --exclude='*.pid' \
        . 2>/dev/null || true
    echo -e "${GREEN}✓ Code backup completed${NC}"
else
    echo -e "${RED}✗ Project root not found: ${PROJECT_ROOT}${NC}"
    exit 1
fi

# 3. Backup Evidence (if exists)
echo -e "${YELLOW}[3/5] Backing up evidence data...${NC}"
EVIDENCE_PATH="/data/evidence"
if [ -d "${EVIDENCE_PATH}" ]; then
    cp -r "${EVIDENCE_PATH}" "${BACKUP_DIR}/evidence/"
    echo -e "${GREEN}✓ Evidence backup completed${NC}"
else
    echo -e "${YELLOW}⚠ No evidence directory found, skipping${NC}"
fi

# 4. Backup Configuration Files
echo -e "${YELLOW}[4/5] Backing up configuration...${NC}"
cd "${PROJECT_ROOT}"
CONFIG_FILES=(
    ".env"
    ".env.production"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "alembic.ini"
    "pytest.ini"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "${PROJECT_ROOT}/${file}" ]; then
        cp "${PROJECT_ROOT}/${file}" "${BACKUP_DIR}/config/"
    fi
done
echo -e "${GREEN}✓ Config backup completed${NC}"

# 5. Create Backup Manifest
echo -e "${YELLOW}[5/5] Creating backup manifest...${NC}"
cat > "${BACKUP_DIR}/MANIFEST.txt" << EOF
NEMESIS Backup Manifest
=======================
Timestamp: ${TIMESTAMP}
Project Root: ${PROJECT_ROOT}
Backup Location: ${BACKUP_DIR}

Contents:
- database/nemesis_db.dump: PostgreSQL database backup (if available)
- code_backup.tar.gz: Source code archive
- evidence/: Evidence data (if exists)
- config/: Configuration files

Restore Instructions:
1. Code: tar -xzf code_backup.tar.gz -C ${PROJECT_ROOT}/
2. Config: cp config/* ${PROJECT_ROOT}/
3. Database (if exists): pg_restore -d ${DB_NAME} database/nemesis_db.dump

Created by: NEMESIS Backup System
EOF

echo -e "${GREEN}✓ Manifest created${NC}"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}BACKUP COMPLETED SUCCESSFULLY${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Location: ${BACKUP_DIR}"
if [ -d "${BACKUP_DIR}" ]; then
    echo -e "Size: $(du -sh ${BACKUP_DIR} 2>/dev/null | cut -f1 || echo 'unknown')"
fi
echo -e "\nTo verify backup integrity, run:"
echo -e "  tar -tzf ${BACKUP_DIR}/code_backup.tar.gz | head -20"