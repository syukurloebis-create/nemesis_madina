#!/usr/bin/env python3
"""
Create Snapshots - Membuat snapshot untuk setiap aggregate
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import json
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool

try:
    from config import settings
except ImportError:
    from config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, poolclass=NullPool)

def create_snapshots():
    print("=" * 60)
    print("📸 CREATING SNAPSHOTS")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Get all cases
        cases = conn.execute(
            text("""
                SELECT 
                    id,
                    title,
                    status,
                    risk_score,
                    risk_level,
                    workflow_stage,
                    created_by,
                    created_at
                FROM cases
            """)
        ).fetchall()
        
        print(f"Found {len(cases)} cases")
        
        total_snapshots = 0
        
        for case in cases:
            case_id = case[0]
            
            # 2. Get evidence for this case
            evidence = conn.execute(
                text("""
                    SELECT id, filename, status, file_hash
                    FROM evidence
                    WHERE case_id = :case_id
                """),
                {"case_id": case_id}
            ).fetchall()
            
            # 3. Get risk explanations
            risk_expl = conn.execute(
                text("""
                    SELECT factor, score, weight, contribution, description
                    FROM risk_explanations
                    WHERE case_id = :case_id
                """),
                {"case_id": case_id}
            ).fetchall()
            
            # 4. Build snapshot data
            snapshot_data = {
                "case": {
                    "id": str(case[0]),
                    "title": case[1],
                    "status": case[2],
                    "risk_score": float(case[3]) if case[3] else 0,
                    "risk_level": case[4],
                    "workflow_stage": case[5],
                    "created_by": str(case[6]) if case[6] else None,
                    "created_at": case[7].isoformat() if case[7] else None
                },
                "evidence": [
                    {
                        "id": str(e[0]),
                        "filename": e[1],
                        "status": e[2],
                        "file_hash": e[3]
                    }
                    for e in evidence
                ],
                "risk_factors": [
                    {
                        "factor": r[0],
                        "score": float(r[1]),
                        "weight": float(r[2]),
                        "contribution": float(r[3]),
                        "description": r[4]
                    }
                    for r in risk_expl
                ],
                "snapshot_timestamp": datetime.now().isoformat()
            }
            
            # 5. Insert snapshot
            conn.execute(
                text("""
                    INSERT INTO snapshots (
                        id, aggregate_id, aggregate_type, 
                        snapshot_version, snapshot_data, 
                        created_at, created_by, tenant_id
                    ) VALUES (
                        :id, :aggregate_id, :aggregate_type,
                        :version, :data,
                        :created_at, :created_by, :tenant_id
                    )
                """),
                {
                    "id": str(uuid.uuid4()),
                    "aggregate_id": case_id,
                    "aggregate_type": "CASE",
                    "version": 1,
                    "data": json.dumps(snapshot_data),
                    "created_at": datetime.now(),
                    "created_by": case[6] if case[6] else None,
                    "tenant_id": "11111111-1111-1111-1111-111111111111"
                }
            )
            
            total_snapshots += 1
            print(f"  ✅ Snapshot created for case {str(case_id)[:8]}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ SNAPSHOTS CREATED! Total: {total_snapshots}")
        print("=" * 60)
        
        # Verifikasi
        result = conn.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT aggregate_id) as aggregates
                FROM snapshots
            """)
        ).fetchone()
        
        print(f"\n📊 Verification:")
        print(f"  Total snapshots: {result[0]}")
        print(f"  Aggregates: {result[1]}")

if __name__ == "__main__":
    create_snapshots()