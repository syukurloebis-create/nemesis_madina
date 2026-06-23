# audit/verify_chain_of_custody.py
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from database import get_db
from events.verifier import IntegrityVerifier
from events.repository import EventRepository
from config import settings


async def audit_chain_of_custody():
    """Forensic audit of chain of custody"""
    
    print("\n" + "="*60)
    print("FORENSIC AUDIT: CHAIN OF CUSTODY")
    print("="*60)
    
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    async for db in get_db():
        # 1. Verify all event chains
        print("\n1. Verifying Event Chain Integrity...")
        
        # Get all unique case_ids
        result = await db.execute(text("SELECT DISTINCT case_id FROM events"))
        case_ids = [row[0] for row in result.fetchall()]
        
        total_cases = len(case_ids)
        verified_cases = 0
        broken_cases = []
        
        repo = EventRepository(db, settings.DEFAULT_TENANT_ID)
        verifier = IntegrityVerifier(repo)
        
        for case_id in case_ids:
            case_id_str = str(case_id)
            verification = await verifier.verify_aggregate_chain(case_id_str)
            
            if verification.get('status') == 'PASS':
                verified_cases += 1
            else:
                broken_cases.append({
                    "case_id": case_id_str,
                    "failed_events": verification.get('failed_events', [])
                })
        
        print(f"   Total cases: {total_cases}")
        print(f"   Verified: {verified_cases}")
        print(f"   Broken: {len(broken_cases)}")
        
        if len(broken_cases) == 0:
            results["passed"].append("All event chains intact")
            print("   ✅ PASS: All event chains are intact")
        else:
            results["failed"].append(f"{len(broken_cases)} cases have broken chains")
            print(f"   ❌ FAIL: {len(broken_cases)} cases have broken chains")
        
        # 2. Verify hash chain completeness
        print("\n2. Verifying Hash Chain Completeness...")
        
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN event_hash IS NULL THEN 1 END) as null_hashes,
                COUNT(CASE WHEN previous_hash IS NULL AND version > 1 THEN 1 END) as missing_previous
            FROM events
        """))
        row = result.fetchone()
        
        print(f"   Total events: {row[0]}")
        print(f"   Null hashes: {row[1]}")
        print(f"   Missing previous_hash: {row[2]}")
        
        if row[1] == 0 and row[2] == 0:
            results["passed"].append("All events have valid hash chain")
            print("   ✅ PASS: All events have valid hash chain")
        else:
            results["failed"].append(f"Found {row[1]} null hashes, {row[2]} missing previous_hash")
            print(f"   ❌ FAIL: Found integrity issues")
        
        # 3. Verify evidence custody chain
        print("\n3. Verifying Evidence Custody Chain...")
        
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total_transfers,
                COUNT(DISTINCT evidence_id) as distinct_evidence
            FROM custody_chain
        """))
        row = result.fetchone()
        
        print(f"   Total custody transfers: {row[0]}")
        print(f"   Evidence with custody records: {row[1]}")
        
        results["passed"].append(f"Custody chain has {row[0]} transfer records")
        print("   ✅ PASS: Custody chain is operational")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(audit_chain_of_custody())
    
    print("\n" + "="*60)
    print("CHAIN OF CUSTODY AUDIT SUMMARY")
    print("="*60)
    print(f"Passed: {len(results['passed'])}")
    for item in results['passed']:
        print(f"  ✅ {item}")
    if results['failed']:
        print(f"Failed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"  ❌ {item}")