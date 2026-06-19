#!/bin/bash

echo "=== Login ==="
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python -c "import sys,json; print(json.load(sys.stdin).get('access_token', ''))")

echo "Token: ${TOKEN:0:50}..."

echo -e "\n=== Create Case ==="
CREATE_RESPONSE=$(curl -s -X POST "http://localhost/cases/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Temporal Test","description":"Testing","priority":"HIGH"}')

echo "Response: $CREATE_RESPONSE"

CASE_ID=$(echo "$CREATE_RESPONSE" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
echo "Case ID: $CASE_ID"

if [ -n "$CASE_ID" ]; then
    echo -e "\n=== Update Status ==="
    curl -s -X PUT "http://localhost/cases/$CASE_ID/status" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"status":"INVESTIGATING"}'
    
    echo -e "\n\n=== Assign Case ==="
    curl -s -X PUT "http://localhost/cases/$CASE_ID/assign" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"assigned_to":"investigator_01"}'
    
    echo -e "\n\n=== Timeline ==="
    curl -s -X GET "http://localhost/temporal/case/$CASE_ID/timeline?limit=10" \
      -H "Authorization: Bearer $TOKEN"
    
    echo -e "\n\n=== Verify Chain ==="
    curl -s -X GET "http://localhost/temporal/case/$CASE_ID/verify-chain" \
      -H "Authorization: Bearer $TOKEN"
    
    echo ""
else
    echo "Failed to create case"
fi
