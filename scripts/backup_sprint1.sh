#!/bin/bash
# Backup sebelum Sprint 1

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/sprint1_${BACKUP_DATE}"

echo "📦 Creating backup: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

# Backup database
echo "🔄 Backing up database..."
docker exec nemesis_madina-postgres-1 pg_dump -U nemesis -d nemesis_db > "${BACKUP_DIR}/database.sql"

# Backup frontend
echo "📁 Backing up frontend..."
cp -r frontend/src "${BACKUP_DIR}/frontend_src"

# Git backup
echo "📝 Creating git backup..."
git checkout -b "backup-sprint1-${BACKUP_DATE}"

echo "✅ Backup complete: ${BACKUP_DIR}"