#!/usr/bin/env python
# scripts/compare_hash_formulas.py
import asyncio
import asyncpg
import json
import hashlib
import os
from datetime import datetime
from typing import Optional, Any

# ============================================================
# VARIAN HASH FORMULAS (KEMUNGKINAN)
# ============================================================

def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)

def canonical_json_no_sort(data: Any) -> str:
    return json.dumps(data, separators=(',', ':'), default=str)

def simple_json(data: Any) -> str:
    return json.dumps(data)

# Varian 1: Hanya aggregate_id + sequence_num + event_type + payload (tanpa occurred_at)
def hash_v1(aggregate_id: str, seq: int, event_type: str, payload: dict, prev_hash: Optional[str]) -> str:
    canonical = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": prev_hash,
    }
    canonical = {k: v for k, v in canonical.items() if v is not None}
    raw = canonical_json(canonical)
    return hashlib.sha256(raw.encode()).hexdigest()

# Varian 2: Dengan occurred_at (string ISO)
def hash_v2(aggregate_id: str, seq: int, event_type: str, payload: dict, prev_hash: Optional[str], occurred_at: str) -> str:
    canonical = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload,
        "occurred_at": occurred_at,
        "previous_hash": prev_hash,
    }
    canonical = {k: v for k, v in canonical.items() if v is not None}
    raw = canonical_json(canonical)
    return hashlib.sha256(raw.encode()).hexdigest()

# Varian 3: Payload sebagai string (bukan dict)
def hash_v3(aggregate_id: str, seq: int, event_type: str, payload_str: str, prev_hash: Optional[str]) -> str:
    canonical = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload_str,
        "previous_hash": prev_hash,
    }
    canonical = {k: v for k, v in canonical.items() if v is not None}
    raw = canonical_json(canonical)
    return hashlib.sha256(raw.encode()).hexdigest()

# Varian 4: Dengan occurred_at sebagai datetime object
def hash_v4(aggregate_id: str, seq: int, event_type: str, payload: dict, prev_hash: Optional[str], occurred_at: datetime) -> str:
    canonical = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload,
        "occurred_at": occurred_at.isoformat(),
        "previous_hash": prev_hash,
    }
    canonical = {k: v for k, v in canonical.items() if v is not None}
    raw = canonical_json(canonical)
    return hashlib.sha256(raw.encode()).hexdigest()

# Varian 5: Tanpa sort_keys (urutan field menentukan hash)
def hash_v5(aggregate_id: str, seq: int, event_type: str, payload: dict, prev_hash: Optional[str]) -> str:
    canonical = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": prev_hash,
    }
    canonical = {k: v for k, v in canonical.items() if v is not None}
    raw = canonical_json_no_sort(canonical)
    return hashlib.sha256(raw.encode()).hexdigest()

# Varian 6: Simple JSON (tanpa separators, tanpa sort_keys)
def hash_v6(aggregate_id: str, seq: int, event_type: str, payload: dict, prev_hash: Optional[str]) -> str:
    data = {
        "aggregate_id": aggregate_id,
        "sequence_num": seq,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": prev_hash,
    }
    raw = simple_json({k: v for k, v in data.items() if v is not None})
    return hashlib.sha256(raw.encode()).hexdigest()


async def compare():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Ambil event pertama dari aggregate rup-65477997
    row = await conn.fetchrow("""
        SELECT 
            aggregate_id,
            sequence_num,
            event_type,
            payload,
            previous_hash,
            occurred_at,
            event_hash as stored_hash
        FROM event_lineage 
        WHERE aggregate_id = 'rup-65477997' AND sequence_num = 1
    """)
    
    await conn.close()
    
    if not row:
        print("❌ Event not found")
        return
    
    stored_hash = row['stored_hash']
    agg_id = row['aggregate_id']
    seq = row['sequence_num']
    event_type = row['event_type']
    prev_hash = row['previous_hash']
    occurred_at = row['occurred_at']
    
    # Payload dalam berbagai format
    payload_dict = row['payload']
    if isinstance(payload_dict, str):
        payload_dict = json.loads(payload_dict)
    payload_str = json.dumps(payload_dict)
    
    print("=" * 80)
    print("🔍 HASH FORMULA COMPARISON")
    print("=" * 80)
    print(f"\n📦 Target Stored Hash: {stored_hash}")
    print(f"\n🔬 Testing variants...\n")
    
    results = []
    
    # Test semua varian
    variants = [
        ("V1: payload dict, tanpa occurred_at", hash_v1(agg_id, seq, event_type, payload_dict, prev_hash)),
        ("V2: payload dict, dengan occurred_at (string)", hash_v2(agg_id, seq, event_type, payload_dict, prev_hash, occurred_at.isoformat())),
        ("V3: payload string, tanpa occurred_at", hash_v3(agg_id, seq, event_type, payload_str, prev_hash)),
        ("V4: payload dict, dengan occurred_at (datetime)", hash_v4(agg_id, seq, event_type, payload_dict, prev_hash, occurred_at)),
        ("V5: tanpa sort_keys", hash_v5(agg_id, seq, event_type, payload_dict, prev_hash)),
        ("V6: simple JSON", hash_v6(agg_id, seq, event_type, payload_dict, prev_hash)),
    ]
    
    for name, computed in variants:
        match = computed == stored_hash
        status = "✅ MATCH" if match else "❌"
        results.append((name, computed, match))
        print(f"{status} {name}")
        print(f"    Computed: {computed}")
        print(f"    Stored:   {stored_hash}\n")
    
    print("=" * 80)
    matches = [r for r in results if r[2]]
    if matches:
        print(f"\n✅ FOUND {len(matches)} MATCHING FORMULA(S):")
        for name, computed, _ in matches:
            print(f"   → {name}")
    else:
        print("\n❌ NO MATCHING FORMULA FOUND")
        print("   Need to investigate further...")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(compare())
