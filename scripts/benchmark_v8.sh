#!/bin/bash
# NEMESIS V8+ Benchmark Script

set -e

echo "=== NEMESIS V8+ Benchmark ==="

# Get current event count
CURRENT_COUNT=$(docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -t -c "SELECT COUNT(*) FROM events" | tr -d ' ')
echo "Current events in database: $CURRENT_COUNT"

# Calculate events needed to reach 1M
NEEDED=$((1000000 - CURRENT_COUNT))
if [ $NEEDED -le 0 ]; then
    echo "Already have 1M+ events. Running verification only."
    NEEDED=0
else
    echo "Need to generate $NEEDED events to reach 1M"
fi

# Run benchmark
python -c "
import asyncio
import time
import uuid
from datetime import datetime
from backend.database import get_db
from backend.events.repository import EventRepository
from backend.config import settings

async def run_benchmark():
    start = time.time()
    count = 0
    
    async for db in get_db(settings.DEFAULT_TENANT_ID):
        repo = EventRepository(db, settings.DEFAULT_TENANT_ID)
        
        # Generate events
        aggregate_id = uuid.uuid4()
        for i in range($NEEDED if $NEEDED > 0 else 10000):
            await repo.append(
                aggregate_id=aggregate_id,
                aggregate_type='test',
                event_type='TEST_EVENT',
                payload={'index': i, 'timestamp': datetime.utcnow().isoformat()},
                metadata={'test': True}
            )
            count += 1
            if count % 1000 == 0:
                print(f'Generated {count} events...')
        
        elapsed = time.time() - start
        print(f'Generated {count} events in {elapsed:.2f} seconds')
        print(f'Rate: {count/elapsed:.2f} events/sec')
        return elapsed, count

elapsed, count = asyncio.run(run_benchmark())
"

echo ""
echo "=== Benchmark Complete ==="
echo "Final event count: $(docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -t -c "SELECT COUNT(*) FROM events" | tr -d ' ')"

echo ""
echo "Gate B Verification:"
echo "Run: python -c \"from backend.events.verifier import IntegrityVerifier; ...\""