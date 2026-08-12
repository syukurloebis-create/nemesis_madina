# backend/scripts/seed_users.py - FIXED

import asyncio
import uuid
from sqlalchemy import text
from backend.infrastructure.database import AsyncSessionLocal
from backend.security.hashing import get_password_hash

async def seed_users():
    async with AsyncSessionLocal() as db:
        # Canonical tenant UUIDs
        tenant_map = {
            "ITJEN": "11111111-1111-1111-1111-111111111111",
            "KPK": "22222222-2222-2222-2222-222222222222",
            "KEJAGUNG": "33333333-3333-3333-3333-333333333333",
            "BPKP": "44444444-4444-4444-4444-444444444444",
        }

        print(f"Using tenants: {tenant_map}")
        
        # Check if users already exist
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count > 0:
            print(f"Users already exist ({count} users). Skipping seed.")
            return
        
        # Users with canonical roles
        users = [
            {"username": "admin", "email": "admin@nemesis.go.id", "full_name": "System Administrator", "password": "Admin123!", "role": "ADMIN", "institution_code": "ITJEN"},
            {"username": "investigator1", "email": "investigator@kpk.go.id", "full_name": "KPK Investigator", "password": "Investigator123!", "role": "INVESTIGATOR", "institution_code": "KPK"},
            {"username": "investigator2", "email": "investigator@kejaksaan.go.id", "full_name": "Kejaksaan Investigator", "password": "Investigator123!", "role": "INVESTIGATOR", "institution_code": "KEJAGUNG"},
            {"username": "viewer", "email": "viewer@bpkp.go.id", "full_name": "BPKP Viewer", "password": "Viewer123!", "role": "VIEWER", "institution_code": "BPKP"}
        ]
        
        from datetime import datetime
        for user_data in users:
            tenant_id = tenant_map.get(user_data["institution_code"])
            if not tenant_id:
                print(f"❌ Tenant not found for {user_data['institution_code']}")
                continue
            
            print(f"Creating user: {user_data['username']} with tenant_id: {tenant_id}")
            
            await db.execute(
                text("""
                    INSERT INTO users (id, username, email, full_name, password_hash, role, tenant_id, is_active, created_at)
                    VALUES (:id, :username, :email, :full_name, :password_hash, :role, :tenant_id, :is_active, :created_at)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "password_hash": get_password_hash(user_data["password"]),
                    "role": user_data["role"],
                    "tenant_id": tenant_id,
                    "is_active": True,
                    "created_at": datetime.utcnow()
                }
            )
        
        await db.commit()
        print(f"✅ Seeded {len(users)} users successfully!")

if __name__ == "__main__":
    asyncio.run(seed_users())