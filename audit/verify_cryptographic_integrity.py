import hashlib
import json
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from backend.database import get_db


async def audit_cryptographic_integrity():
    """Forensic audit of cryptographic evidence preservation"""
    
    print("\n" + "="*60)
    print("FORENSIC AUDIT: CRYPTOGRAPHIC INTEGRITY")
    print("="*60)
    
    results = {"passed": [], "failed": [], "warnings": []}
    
    async for db in get_db():
        # 1. Verify SHA256 hash integrity
        print("\n1. Verifying SHA256 Hash Integrity...")
        
        # Get total event count
        result = await db.execute(text("SELECT COUNT(*) FROM events"))
        total_events = result.scalar()
        
        if total_events == 0:
            print("   No events found in database")
            results["warnings"].append("No events to verify")
            return results
        
        # Sample random events for hash verification (up to 100)
        sample_size = min(100, total_events)
        result = await db.execute(text("""
            SELECT id, event_id, event_type, data, timestamp, version, event_hash
            FROM events 
            ORDER BY random() 
            LIMIT $1
        """), (sample_size,))
        samples = result.fetchall()
        
        mismatches = 0
        for sample in samples:
            # Recalculate hash
            data = sample[3]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    pass
            
            block = {
                "event_id": str(sample[1]),
                "event_type": sample[2],
                "data": data,
                "timestamp": sample[4].isoformat() if sample[4] else None,
                "version": sample[5]
            }
            canonical = json.dumps(block, sort_keys=True, separators=(',', ':'))
            calculated = hashlib.sha256(canonical.encode()).hexdigest()
            
            if calculated != sample[6]:
                mismatches += 1
        
        print(f"   Total events in database: {total_events}")
        print(f"   Sampled events: {len(samples)}")
        print(f"   Hash mismatches: {mismatches}")
        
        if mismatches == 0:
            results["passed"].append("SHA256 hash integrity verified")
            print("   ✅ PASS: All sampled hashes are valid")
        else:
            results["failed"].append(f"Found {mismatches} hash mismatches")
            print(f"   ❌ FAIL: {mismatches} hash mismatches detected")
        
        # 2. Verify chain linkage
        print("\n2. Verifying Chain Linkage...")
        
        result = await db.execute(text("""
            SELECT COUNT(*) 
            FROM events e1
            JOIN events e2 ON e2.case_id = e1.case_id AND e2.version = e1.version + 1
            WHERE e2.previous_hash != e1.event_hash
        """))
        broken_links = result.scalar()
        
        print(f"   Broken chain links: {broken_links}")
        
        if broken_links == 0:
            results["passed"].append("All chain links are valid")
            print("   ✅ PASS: All chain links are valid")
        else:
            results["failed"].append(f"Found {broken_links} broken chain links")
            print(f"   ❌ FAIL: {broken_links} broken chain links detected")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(audit_cryptographic_integrity())
    
    print("\n" + "="*60)
    print("CRYPTOGRAPHIC INTEGRITY AUDIT SUMMARY")
    print("="*60)
    for item in results['passed']:
        print(f"  ✅ {item}")
    for item in results['failed']:
        print(f"  ❌ {item}")
