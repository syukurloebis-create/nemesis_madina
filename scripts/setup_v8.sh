#!/bin/bash
# NEMESIS V8+ Setup Script for Existing Database

set -e

echo "=== NEMESIS V8+ Setup ==="
echo "This script will enhance your existing database for V8+ features"

# Check if PostgreSQL is running
if ! docker ps | grep -q postgres; then
    echo "Error: PostgreSQL container not running"
    echo "Please start your containers first"
    exit 1
fi

# Create sequence for commit position
echo "Creating global_audit_seq sequence..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
CREATE SEQUENCE IF NOT EXISTS global_audit_seq;
"

# Add enhancement columns to events table
echo "Enhancing events table..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
ALTER TABLE events ADD COLUMN IF NOT EXISTS event_hash VARCHAR(64);
ALTER TABLE events ADD COLUMN IF NOT EXISTS aggregate_hash VARCHAR(64);
ALTER TABLE events ADD COLUMN IF NOT EXISTS previous_hash VARCHAR(64);
ALTER TABLE events ADD COLUMN IF NOT EXISTS event_signature TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS signing_key_id UUID;
ALTER TABLE events ADD COLUMN IF NOT EXISTS commit_position BIGSERIAL UNIQUE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS event_version INTEGER DEFAULT 1;
"

# Add columns to snapshots table
echo "Enhancing snapshots table..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
ALTER TABLE snapshots ADD COLUMN IF NOT EXISTS snapshot_version INTEGER DEFAULT 1;
ALTER TABLE snapshots ADD COLUMN IF NOT EXISTS snapshot_hash VARCHAR(64);
"

# Create indexes for performance
echo "Creating performance indexes..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_commit ON events(commit_position);
"

# Backfill event_hash for existing events
echo "Backfilling event_hash for existing events..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
DO \$\$
DECLARE
    ev RECORD;
BEGIN
    FOR ev IN SELECT id, aggregate_id, event_type, payload, metadata, created_at FROM events WHERE event_hash IS NULL
    LOOP
        UPDATE events SET event_hash = encode(sha256(
            (jsonb_build_object(
                'event_id', ev.id::text,
                'aggregate_id', ev.aggregate_id::text,
                'event_type', ev.event_type,
                'payload', ev.payload,
                'metadata', ev.metadata,
                'timestamp', ev.created_at::text
            )::text)::bytea
        ), 'hex')
        WHERE id = ev.id;
    END LOOP;
END \$\$;
"

echo "=== Setup complete ==="
echo ""
echo "Current tables in database:"
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "\dt"

echo ""
echo "NEMESIS V8+ is ready!"
echo "Start the API with: uvicorn backend.main:app --reload"