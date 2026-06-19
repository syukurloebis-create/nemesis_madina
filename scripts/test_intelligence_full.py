import asyncio
from backend.infrastructure.database import AsyncSessionLocal
from backend.intelligence.service import IntelligenceService

async def run():
    async with AsyncSessionLocal() as session:
        service = IntelligenceService(session)

        # ambil 1 case nyata dari DB
        result = await session.execute("SELECT id FROM cases LIMIT 1")
        case_id = result.scalar()

        if not case_id:
            print("❌ No case found")
            return

        print(f"🧠 Testing case: {case_id}")

        output = await service.analyze_case(case_id)

        print("\n===== INTELLIGENCE OUTPUT =====")
        print(output)

if __name__ == "__main__":
    asyncio.run(run())