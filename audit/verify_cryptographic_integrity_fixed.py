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
        # 1. Get total event count
        print("\n1. Database Statistics...")
        
        result = await db.execute(text("SELECT COUNT(*) FROM events"))
        total_events = result.scalar()
        print(f"   Total events in database: {total_events}")
        
        if total_events == 0:
            results["warnings"].append("No events found in database")
            return results
        
        # 2. Verify hash chain linkage
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
        
        # 3. Check for null hashes
        print("\n3. Checking for Null Hashes...")
        
        result = await db.execute(text("""
            SELECT COUNT(CASE WHEN event_hash IS NULL THEN 1 END) as null_hashes,
                   COUNT(CASE WHEN previous_hash IS NULL AND version > 1 THEN 1 END) as missing_previous
            FROM events
        """))
        row = result.fetchone()
        null_hashes = row[0]
        missing_previous = row[1]
        
        print(f"   Null event hashes: {null_hashes}")
        print(f"   Missing previous_hash: {missing_previous}")
        
        if null_hashes == 0 and missing_previous == 0:
            results["passed"].append("No null hashes or missing previous_hash")
            print("   ✅ PASS: All hashes are present")
        else:
            results["failed"].append(f"Found {null_hashes} null hashes, {missing_previous} missing previous")
            print("   ❌ FAIL: Missing hash data detected")
    
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
