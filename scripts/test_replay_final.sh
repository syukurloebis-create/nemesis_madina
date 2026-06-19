#!/bin/bash

echo "=========================================="
echo "REPLAY API TEST - Final Version"
echo "=========================================="

# Step 1: Insert case directly into database
echo -e "\n📝 Creating case directly in database..."
CASE_ID=$(docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -t -c "
INSERT INTO cases (id, title, description, status, created_at, updated_at)
VALUES (gen_random_uuid(), 'Replay Test Case', 'Testing replay functionality', 'active', NOW(), NOW())
RETURNING id;
" | tr -d ' ')

echo "✅ Case created with ID: $CASE_ID"

# Step 2: Add events to event store
echo -e "\n📝 Adding events to event store..."
docker exec -i nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db <<SQL
INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id)
VALUES 
  (gen_random_uuid(), '$CASE_ID', 'case_created', '{"title": "Replay Test Case", "description": "Testing replay"}', NOW(), 1, 'system'),
  (gen_random_uuid(), '$CASE_ID', 'case_assigned', '{"assignee": "investigator_01"}', NOW(), 2, 'system'),
  (gen_random_uuid(), '$CASE_ID', 'evidence_added', '{"evidence_id": "evid_001", "title": "Financial Report"}', NOW(), 3, 'system');
SQL
echo "✅ 3 events added to event store"

# Step 3: Wait a moment for indexes to update
sleep 1

# Step 4: Verify events were inserted
echo -e "\n📊 Verifying events in database..."
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -c "
SELECT version, event_type, data FROM events WHERE case_id = '$CASE_ID' ORDER BY version;
"

# Step 5: Test history endpoint
echo -e "\n📡 Testing /replay/case/{id}/history..."
HISTORY_RESPONSE=$(curl -s "http://localhost/replay/case/${CASE_ID}/history")
echo "$HISTORY_RESPONSE" | jq .

# Step 6: Test replay endpoint
echo -e "\n📡 Testing /replay/case/{id}/replay..."
REPLAY_RESPONSE=$(curl -s "http://localhost/replay/case/${CASE_ID}/replay")
echo "$REPLAY_RESPONSE" | jq .

# Step 7: Test timeline
echo -e "\n📡 Testing /replay/case/{id}/timeline..."
TIMELINE_RESPONSE=$(curl -s "http://localhost/replay/case/${CASE_ID}/timeline")
echo "$TIMELINE_RESPONSE" | jq .

# Step 8: Test specific version
echo -e "\n📡 Testing /replay/case/{id}/version/2..."
VERSION_RESPONSE=$(curl -s "http://localhost/replay/case/${CASE_ID}/version/2")
echo "$VERSION_RESPONSE" | jq .

# Step 9: Test state at version
echo -e "\n📡 Testing /replay/case/{id}/state/version/2..."
STATE_RESPONSE=$(curl -s "http://localhost/replay/case/${CASE_ID}/state/version/2")
echo "$STATE_RESPONSE" | jq .

echo -e "\n=========================================="
echo "✅ TEST COMPLETED"
echo "Case ID: $CASE_ID"
echo "=========================================="
