import asyncio
import asyncpg
import os

# Gunakan DSN tanpa +asyncpg
PG_DSN = "postgresql://nemesis:nemesis123@postgres:5432/nemesis_db"

async def test():
    conn = await asyncpg.connect(PG_DSN)
    count = await conn.fetchval("SELECT COUNT(*) FROM graph_entities")
    print(f"✅ Total entities: {count}")
    await conn.close()
    print("✅ Intelligence test passed!")

if __name__ == "__main__":
    asyncio.run(test())
