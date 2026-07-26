#!/bin/bash
# Rollback Sprint 1

if [ -z "$1" ]; then
  echo "Usage: ./rollback_sprint1.sh <backup-directory>"
  echo "Available backups:"
  ls -la ./backups/
  exit 1
fi

BACKUP_DIR=$1

echo "🔙 Rolling back to: ${BACKUP_DIR}"

# Stop frontend
echo "🛑 Stopping frontend..."
docker-compose stop frontend

# Restore frontend
echo "📥 Restoring frontend..."
rm -rf frontend/src
cp -r "${BACKUP_DIR}/frontend_src" frontend/src

# Restore database
echo "🔄 Restoring database..."
docker exec -i nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db < "${BACKUP_DIR}/database.sql"

# Rebuild frontend
echo "🔨 Rebuilding frontend..."
docker-compose build frontend

# Start frontend
echo "▶️ Starting frontend..."
docker-compose up -d frontend

echo "✅ Rollback complete"