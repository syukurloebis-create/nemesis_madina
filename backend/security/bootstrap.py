from sqlalchemy import select
from passlib.context import CryptContext

from security.models import User
from infrastructure.database import AsyncSessionLocal

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

async def ensure_admin():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(User).where(
                User.username == "admin"
            )
        )

        admin = result.scalar_one_or_none()

        if admin:
            return

        user = User(
            username="admin",
            email="admin@nemesis.local",
            full_name="System Administrator",
            password_hash=pwd.hash("Admin123!"),
            role="ADMIN",
            is_active=True,
        )

        db.add(user)

        await db.commit()

        print(
            "✓ Default admin created"
        )