#!/bin/bash
# Emergency rollback script

BACKUP_DATE=$1

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: ./scripts/emergency_rollback.sh YYYYMMDD"
    echo "Available backups:"
    ls backups/final/
    exit 1
fi

echo "⚠️ EMERGENCY ROLLBACK to $BACKUP_DATE"

# Stop services
pkill -f uvicorn 2>/dev/null
pkill -f worker_outbox 2>/dev/null

# Restore database
cp "backups/final/nemesis_${BACKUP_DATE}.db" nemesis.db

# Restart
./scripts/start_server.sh

echo "✅ Rollback complete"
