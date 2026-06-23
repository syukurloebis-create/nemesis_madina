# backend/scripts/seed_users.py
import asyncio
import uuid
from sqlalchemy import text
from infrastructure.database import AsyncSessionLocal
from security.hashing import get_password_hash

async def seed_users():
    async with AsyncSessionLocal() as db:
        # Institution IDs (hardcoded)
        institutions = {
            "ITJEN": "inspektorat-1",
            "BPKP": "bpkp-1", 
            "KEJAGUNG": "kejaksaan-1",
            "KPK": "kpk-1"
        }
        
        print(f"Using institutions: {institutions}")
        
        # Check if users already exist
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count > 0:
            print(f"Users already exist ({count} users). Skipping seed.")
            return
        
        # Users with hardcoded institution IDs
        users = [
            {"username": "admin", "email": "admin@nemesis.go.id", "full_name": "System Administrator", "password": "Admin123!", "role": "ADMIN", "institution_code": "ITJEN"},
            {"username": "auditor", "email": "auditor@inspektorat.go.id", "full_name": "Auditor Inspektorat", "password": "Auditor123!", "role": "AUDITOR", "institution_code": "ITJEN"},
            {"username": "investigator", "email": "investigator@kpk.go.id", "full_name": "KPK Investigator", "password": "Investigator123!", "role": "INVESTIGATOR", "institution_code": "KPK"},
            {"username": "prosecutor", "email": "prosecutor@kejaksaan.go.id", "full_name": "Kejaksaan Prosecutor", "password": "Prosecutor123!", "role": "PROSECUTOR", "institution_code": "KEJAGUNG"},
            {"username": "viewer", "email": "viewer@bpkp.go.id", "full_name": "BPKP Viewer", "password": "Viewer123!", "role": "VIEWER", "institution_code": "BPKP"}
        ]
        
        from datetime import datetime
        for user_data in users:
            institution_id = institutions.get(user_data["institution_code"])
            if not institution_id:
                print(f"❌ Institution not found for {user_data['institution_code']}")
                continue
            
            print(f"Creating user: {user_data['username']} with institution_id: {institution_id}")
            
            await db.execute(
                text("""
                    INSERT INTO users (id, username, email, full_name, password_hash, role, institution_id, is_active, is_verified, created_at)
                    VALUES (:id, :username, :email, :full_name, :password_hash, :role, :institution_id, :is_active, :is_verified, :created_at)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "password_hash": get_password_hash(user_data["password"]),
                    "role": user_data["role"],
                    "institution_id": institution_id,
                    "is_active": True,
                    "is_verified": True,
                    "created_at": datetime.utcnow()
                }
            )
        
        await db.commit()
        print(f"✅ Seeded {len(users)} users successfully!")

if __name__ == "__main__":
    asyncio.run(seed_users())
