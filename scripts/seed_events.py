#!/usr/bin/env python3
"""
Seed events untuk testing event sourcing
Membangun dataset uji dengan 20-50 events per case
"""

import asyncio
import asyncpg
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Database connection
DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

# Event types untuk testing
EVENT_TYPES = [
    "CASE_CREATED",
    "CASE_ASSIGNED", 
    "CASE_UPDATED",
    "EVIDENCE_ADDED",
    "EVIDENCE_VERIFIED",
    "FINDING_CREATED",
    "CASE_ESCALATED",
    "CASE_REVIEWED",
    "CASE_CLOSED"
]

# Sample data generators
def generate_case_data() -> Dict:
    return {
        "title": f"Investigasi Kasus {random.randint(1000, 9999)}",
        "description": f"Deskripsi kasus untuk testing event sourcing",
        "priority": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
        "category": random.choice(["FRAUD", "CORRUPTION", "MONEY_LAUNDERING", "TERRORISM"])
    }

def generate_assignee_data() -> Dict:
    return {
        "assignee": random.choice(["investigator_01", "investigator_02", "investigator_03", "forensic_team"]),
        "role": random.choice(["LEAD", "SUPPORT", "REVIEWER"])
    }

def generate_evidence_data() -> Dict:
    return {
        "evidence_id": f"EVID_{uuid.uuid4().hex[:8].upper()}",
        "title": f"Bukti {random.choice(['Digital', 'Dokumen', 'Saksi', 'CCTV', 'Financial'])}",
        "type": random.choice(["DOCUMENT", "IMAGE", "VIDEO", "AUDIO", "FINANCIAL"]),
        "hash": uuid.uuid4().hex,
        "source": random.choice(["FORENSIC_LAB", "FIELD", "THIRD_PARTY"])
    }

def generate_finding_data() -> Dict:
    return {
        "finding_id": f"FIND_{uuid.uuid4().hex[:8].upper()}",
        "title": f"Temuan {random.choice(['Anomali', 'Pattern', 'Relationship', 'Transaction'])}",
        "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
        "description": "Deskripsi temuan dari analisis"
    }

def generate_update_data() -> Dict:
    return {
        "field": random.choice(["title", "description", "priority", "category"]),
        "old_value": "previous value",
        "new_value": "updated value",
        "reason": random.choice(["new_evidence", "reclassification", "correction"])
    }

async def create_test_case(conn, institution_id: str) -> str:
    """Create a test case and return its ID"""
    case_id = str(uuid.uuid4())
    case_data = generate_case_data()
    
    await conn.execute("""
        INSERT INTO cases (id, title, description, status, priority, category, institution_id, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
    """, case_id, case_data["title"], case_data["description"], "ACTIVE", 
        case_data["priority"], case_data["category"], institution_id)
    
    return case_id

async def add_event(conn, case_id: str, event_type: str, data: Dict, version: int, user_id: str, timestamp: datetime):
    """Add an event to the event store"""
    event_id = str(uuid.uuid4())
    await conn.execute("""
        INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """, event_id, case_id, event_type, data, timestamp, version, user_id)
    return event_id

async def generate_event_sequence(case_id: str, num_events: int = 30) -> List[Dict]:
    """Generate realistic event sequence for a case"""
    events = []
    base_time = datetime.now() - timedelta(days=30)
    
    # Case Created (always first)
    events.append({
        "type": "CASE_CREATED",
        "data": generate_case_data(),
        "user": "system"
    })
    
    # Assign investigator
    events.append({
        "type": "CASE_ASSIGNED",
        "data": generate_assignee_data(),
        "user": "admin"
    })
    
    # Random events
    for i in range(num_events - 2):
        event_type = random.choice(EVENT_TYPES[2:])  # Skip CASE_CREATED and CASE_ASSIGNED
        
        if event_type == "EVIDENCE_ADDED":
            data = generate_evidence_data()
        elif event_type == "EVIDENCE_VERIFIED":
            data = {"verified_by": "forensic_lab", "status": "VERIFIED"}
        elif event_type == "FINDING_CREATED":
            data = generate_finding_data()
        elif event_type == "CASE_UPDATED":
            data = generate_update_data()
        elif event_type == "CASE_ESCALATED":
            data = {"reason": "complex_pattern", "escalated_to": "supervisor"}
        elif event_type == "CASE_REVIEWED":
            data = {"reviewer": "quality_assurance", "comments": "Review comments"}
        elif event_type == "CASE_CLOSED":
            data = {"resolution": "PROSECUTION", "closed_by": "judge"}
        else:
            data = {"status": "UPDATED"}
        
        # Random timestamp progression
        timestamp = base_time + timedelta(days=random.randint(1, 30), 
                                          hours=random.randint(0, 23),
                                          minutes=random.randint(0, 59))
        
        events.append({
            "type": event_type,
            "data": data,
            "user": random.choice(["investigator_01", "forensic_analyst", "supervisor", "admin"]),
            "timestamp": timestamp
        })
    
    # Sort by timestamp
    events.sort(key=lambda x: x.get("timestamp", base_time))
    
    # Add version numbers
    for idx, event in enumerate(events, 1):
        event["version"] = idx
    
    return events

async def main():
    print("=" * 70)
    print("NEMESIS MADINA - SEED EVENTS SCRIPT")
    print("=" * 70)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Get or create institution
    institution_id = str(uuid.uuid4())
    await conn.execute("""
        INSERT INTO institutions (id, name, code, type, created_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (code) DO NOTHING
    """, institution_id, "Audit Test Institution", "AUDIT001", "TESTING")
    
    # Get existing institution
    result = await conn.fetchrow("SELECT id FROM institutions WHERE code = 'AUDIT001'")
    if result:
        institution_id = result["id"]
    
    print(f"\n📋 Using Institution ID: {institution_id}")
    
    # Create 5 test cases with 20-50 events each
    test_cases = []
    for case_num in range(1, 6):
        print(f"\n📝 Creating Case {case_num}...")
        
        case_id = await create_test_case(conn, institution_id)
        num_events = random.randint(20, 50)
        
        print(f"   Case ID: {case_id}")
        print(f"   Events: {num_events}")
        
        # Generate event sequence
        events = await generate_event_sequence(case_id, num_events)
        
        # Insert events
        for event in events:
            await add_event(
                conn, case_id, event["type"], event["data"], 
                event["version"], event["user"], 
                event.get("timestamp", datetime.now())
            )
        
        print(f"   ✅ Inserted {len(events)} events")
        
        # Create snapshots at every 10 events
        for version in range(10, len(events) + 1, 10):
            # Get state up to this version
            state_events = [e for e in events if e["version"] <= version]
            
            # Build state (simplified for snapshot)
            snapshot_state = {
                "case_id": case_id,
                "version": version,
                "event_count": len(state_events),
                "last_event_type": state_events[-1]["type"],
                "snapshot_created_at": datetime.now().isoformat()
            }
            
            await conn.execute("""
                INSERT INTO event_snapshots (case_id, snapshot_data, snapshot_version, event_count, created_at)
                VALUES ($1, $2, $3, $4, NOW())
            """, case_id, snapshot_state, version, len(state_events))
        
        print(f"   📸 Created snapshots every 10 events")
        test_cases.append({"id": case_id, "events": len(events)})
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SEED DATA SUMMARY")
    print("=" * 70)
    
    total_events = 0
    for case in test_cases:
        total_events += case["events"]
        print(f"Case {case['id'][:8]}...: {case['events']} events")
    
    print(f"\n✅ Total Cases: {len(test_cases)}")
    print(f"✅ Total Events: {total_events}")
    print(f"✅ Average Events/Case: {total_events // len(test_cases)}")
    
    # Verify counts
    result = await conn.fetchrow("SELECT COUNT(*) as count FROM events")
    print(f"\n📈 Database verification: {result['count']} total events")
    
    result = await conn.fetchrow("SELECT COUNT(DISTINCT case_id) as count FROM events")
    print(f"📈 Cases with events: {result['count']}")
    
    result = await conn.fetchrow("SELECT COUNT(*) as count FROM event_snapshots")
    print(f"📸 Snapshots created: {result['count']}")
    
    await conn.close()
    
    print("\n" + "=" * 70)
    print("✅ SEED DATA COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    # Save case IDs for later tests
    with open("/tmp/test_cases.txt", "w") as f:
        for case in test_cases:
            f.write(f"{case['id']}\n")
    
    print("\n📝 Test case IDs saved to: /tmp/test_cases.txt")

if __name__ == "__main__":
    asyncio.run(main())
