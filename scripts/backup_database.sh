#!/bin/bash
# ============================================================================
# NEMESIS Database Backup Script
# ============================================================================

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nemesis_db_$TIMESTAMP.sql"

echo "Backing up database to: $BACKUP_FILE"

# Check if pg_dump is available
if command -v pg_dump &> /dev/null; then
    pg_dump -h localhost -U nemesis -d nemesis_db -f "$BACKUP_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        gzip "$BACKUP_FILE"
        echo "[OK] Backup completed: ${BACKUP_FILE}.gz"
    else
        echo "[FAIL] Backup failed"
        exit 1
    fi
else
    echo "[WARN] pg_dump not found - skipping database backup"
fi

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete 2>/dev/null

echo ""
echo "Backup location: $BACKUP_DIR"
