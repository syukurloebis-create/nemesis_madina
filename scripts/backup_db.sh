#!/bin/bash
# Backup script untuk Windows (Git Bash)

BACKUP_DIR="/c/nemesis_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/nemesis_db_$TIMESTAMP.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup to $BACKUP_FILE"

# Check container
CONTAINER=$(docker ps --format "{{.Names}}" | grep postgres | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ PostgreSQL container not found"
    exit 1
fi

echo "Found container: $CONTAINER"

# Backup
docker exec $CONTAINER pg_dump -U nemesis -d nemesis_db > "$BACKUP_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Backup completed: $BACKUP_FILE"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "   Size: $SIZE"
    
    # Optionally compress
    if command -v gzip &> /dev/null; then
        gzip -f "$BACKUP_FILE"
        echo "✅ Compressed: ${BACKUP_FILE}.gz"
    fi
else
    echo "❌ Backup failed"
    cat "$BACKUP_FILE"
    exit 1
fi

echo "✅ Backup process completed"
