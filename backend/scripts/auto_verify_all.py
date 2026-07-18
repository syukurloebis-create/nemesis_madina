#!/usr/bin/env python3
"""
Auto-verify all pending evidence
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import get_db
from backend.services.auto_verifier import AutoVerifier

async def auto_verify_all():
    """Auto-verify all pending evidence"""
    async for db in get_db():
        # Get all pending evidence
        result = await db.execute(text("""
            SELECT id, filename, file_hash, file_size, file_type
            FROM evidence 
            WHERE status = 'pending'
        """))
        pending = result.fetchall()
        
        print(f"📊 Found {len(pending)} pending evidence")
        
        verified_count = 0
        for row in pending:
            evidence_id = row[0]
            result = await AutoVerifier.verify_evidence(evidence_id, db)
            if result.get("status") == "verified":
                verified_count += 1
                print(f"  ✅ Verified: {row[1]}")
            else:
                print(f"  ⚠️ Failed: {row[1]} - {result.get('reason', 'unknown')}")
        
        print(f"\n✅ Auto-verified {verified_count} evidence")
        
        # Final stats
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'verified' THEN 1 END) as verified,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
            FROM evidence
        """))
        row = result.fetchone()
        print(f"\n📊 FINAL STATS:")
        print(f"  Total: {row[0]}")
        print(f"  Verified: {row[1]}")
        print(f"  Pending: {row[2]}")
        print(f"  Verification Rate: {row[1]/row[0]*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(auto_verify_all())
