#!/bin/bash
# ============================================================================
# NEMESIS Restore Script
# ============================================================================

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_NAME="${1:-latest}"

# Function to find latest backup
find_latest_backup() {
    ls -t "$BACKUP_DIR"/nemesis_backup_*.sql.gz 2>/dev/null | head -1
}

# Check if backups directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    echo "   Create it with: mkdir -p $BACKUP_DIR"
    exit 1
fi

# Handle latest backup
if [ "$BACKUP_NAME" = "latest" ]; then
    LATEST=$(find_latest_backup)
    if [ -n "$LATEST" ]; then
        BACKUP_NAME=$(basename "$LATEST" | sed 's/_backup.*//')
        echo "Found latest backup: $BACKUP_NAME"
    else
        echo "❌ No backups found in $BACKUP_DIR"
        echo ""
        echo "Available files in $BACKUP_DIR:"
        ls -la "$BACKUP_DIR" 2>/dev/null || echo "  (empty)"
        echo ""
        echo "To create a backup first, run: ./scripts/backup.sh"
        exit 1
    fi
fi

echo "============================================================"
echo "NEMESIS RESTORE"
echo "============================================================"
echo "  Backup: $BACKUP_NAME"
echo ""

read -p "Are you sure? This will overwrite current data! (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Restore database
echo ""
echo "[1/3] Restoring database..."
DB_FILE="$BACKUP_DIR/${BACKUP_NAME}_backup.sql.gz"
if [ -f "$DB_FILE" ]; then
    if command -v gunzip &> /dev/null && command -v psql &> /dev/null; then
        gunzip -c "$DB_FILE" | psql "$DATABASE_URL" 2>/dev/null
        echo "  ✅ Database restored"
    else
        echo "  ⚠️ Required tools not available (gunzip or psql)"
    fi
else
    echo "  ⚠️ Database backup not found: $DB_FILE"
fi

# Restore evidence
echo ""
echo "[2/3] Restoring evidence..."
EVIDENCE_FILE="$BACKUP_DIR/${BACKUP_NAME}_backup_evidence.tar.gz"
if [ -f "$EVIDENCE_FILE" ]; then
    if command -v tar &> /dev/null; then
        tar -xzf "$EVIDENCE_FILE" -C ./
        echo "  ✅ Evidence restored"
    else
        echo "  ⚠️ tar not available"
    fi
else
    echo "  ⚠️ Evidence backup not found"
fi

# Restore configuration
echo ""
echo "[3/3] Restoring configuration..."
CONFIG_FILE="$BACKUP_DIR/${BACKUP_NAME}_backup_config.tar.gz"
if [ -f "$CONFIG_FILE" ]; then
    if command -v tar &> /dev/null; then
        tar -xzf "$CONFIG_FILE" -C ./
        echo "  ✅ Configuration restored"
    else
        echo "  ⚠️ tar not available"
    fi
else
    echo "  ⚠️ Config backup not found"
fi

# Restart services (optional)
echo ""
read -p "Restart services? (yes/no): " RESTART
if [ "$RESTART" = "yes" ]; then
    echo "Restarting services..."
    ./scripts/stop_server.sh 2>/dev/null
    sleep 2
    ./scripts/start_server.sh
fi

echo ""
echo "============================================================"
echo "RESTORE COMPLETE"
echo "============================================================"
