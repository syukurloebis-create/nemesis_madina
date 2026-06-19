#!/usr/bin/env python3
import asyncio
import asyncpg
import uuid
from datetime import datetime

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

async def seed():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # 1. Buat institution dulu
    inst_id = str(uuid.uuid4())
    await conn.execute("""
        INSERT INTO institutions (id, name, type, code)
        VALUES ($1, 'Test Institution', 'OTHER', 'TEST-001')
        ON CONFLICT (code) DO NOTHING
    """, inst_id)
    
    # 2. Buat case
    case_id = str(uuid.uuid4())
    await conn.execute("""
        INSERT INTO cases (id, title, description, status, priority, case_metadata, institution_id)
        VALUES ($1, 'Integrated Test Case', 'Created by consistent seed', 'DRAFT', 'MEDIUM', '{}', $2)
    """, case_id, inst_id)
    
    # 3. Buat event untuk case yang sama
    await conn.execute("""
        INSERT INTO events (event_id, case_id, event_type, version, created_at)
        VALUES (gen_random_uuid(), $1, 'case_created', 1, NOW())
    """, case_id)
    
    print(f"✅ Created case: {case_id} with event")
    await conn.close()

asyncio.run(seed())
