# benchmarks/test_rebuild.py
import asyncio
import sys
import time
sys.path.insert(0, '.')

from sqlalchemy import text
from backend.database import get_db
from backend.projections.engine import ProjectionEngine
from backend.config import settings


async def test_rebuild(case_id: str):
    """Test projection rebuild performance"""
    
    print(f"\n=== Testing Rebuild for Case: {case_id} ===")
    
    async for db in get_db():
        # Get event count first - FIX: wrap SQL with text()
        result = await db.execute(
            text("SELECT COUNT(*) FROM events WHERE case_id = :case_id"),
            {"case_id": case_id}
        )
        event_count = result.scalar()
        print(f"Total events: {event_count:,}")
        
        if event_count == 0:
            print("No events found for this case")
            return {"event_count": 0, "rebuild_time": 0}
        
        # Test rebuild
        print("\n🔄 Running projection rebuild...")
        engine = ProjectionEngine(db)
        
        start = time.time()
        await engine.rebuild_projection("case_projection", batch_size=10000)
        rebuild_time = time.time() - start
        
        print(f"\n✅ Rebuild complete!")
        print(f"   Time: {rebuild_time:.2f} seconds")
        print(f"   Speed: {event_count / rebuild_time:.2f} events/sec")
        
        # Check Gate B criteria
        if event_count >= 1000000:
            if rebuild_time <= 600:
                print(f"\n✅ G2 (rebuild_1M ≤ 10min): {rebuild_time:.2f}s → PASS")
            else:
                print(f"\n❌ G2 (rebuild_1M ≤ 10min): {rebuild_time:.2f}s → FAIL")
        
        return {"event_count": event_count, "rebuild_time": rebuild_time}


if __name__ == "__main__":
    case_id = sys.argv[1] if len(sys.argv) > 1 else "18cea8e0-e9a0-474e-a7f0-e3af8181b1d5"
    result = asyncio.run(test_rebuild(case_id))
    print(f"\nResult: {result}")