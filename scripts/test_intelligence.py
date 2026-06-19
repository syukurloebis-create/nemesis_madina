import asyncio
from backend.infrastructure.database import AsyncSessionLocal
from backend.intelligence.service import IntelligenceService


async def run_test():
    async with AsyncSessionLocal() as session:
        service = IntelligenceService(session)

        # ganti dengan case_id yang valid di DB kamu
        case_id = "test-case-001"

        try:
            result = await service.analyze_case(case_id)

            print("\n===== INTELLIGENCE RESULT =====")
            print(result)

        except Exception as e:
            print("\n===== ERROR =====")
            print(str(e))


if __name__ == "__main__":
    asyncio.run(run_test())