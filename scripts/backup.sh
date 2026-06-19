#!/bin/bash
# ============================================================================
# NEMESIS Backup Script
# ============================================================================

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="nemesis_backup_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

echo "============================================================"
echo "NEMESIS BACKUP"
echo "============================================================"
echo ""

# Backup database
echo "[1/3] Backing up database..."
if command -v pg_dump &> /dev/null && [ -n "$DATABASE_URL" ]; then
    pg_dump "$DATABASE_URL" -f "$BACKUP_DIR/${BACKUP_NAME}.sql"
    gzip "$BACKUP_DIR/${BACKUP_NAME}.sql"
    echo "  ✅ Database backup: ${BACKUP_NAME}.sql.gz"
else
    echo "  ⚠️ pg_dump not available, skipping database backup"
fi

# Backup evidence
echo ""
echo "[2/3] Backing up evidence..."
if [ -d "./evidence_data" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_evidence.tar.gz" ./evidence_data/
    echo "  ✅ Evidence backup: ${BACKUP_NAME}_evidence.tar.gz"
else
    echo "  ⚠️ No evidence directory found"
fi

# Backup configuration
echo ""
echo "[3/3] Backing up configuration..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" \
    .env.production \
    docker-compose.yml \
    nginx.conf 2>/dev/null || true
echo "  ✅ Configuration backup: ${BACKUP_NAME}_config.tar.gz"

echo ""
echo "============================================================"
echo "BACKUP COMPLETE"
echo "============================================================"
echo "  Location: $BACKUP_DIR"
echo "  Name: $BACKUP_NAME"
echo "============================================================"