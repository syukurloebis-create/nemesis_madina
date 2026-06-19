"""Register a demo webhook for testing"""

import asyncio
import aiohttp
import sys

async def register_webhook():
    webhook_data = {
        "name": "APIP_Production",
        "url": "https://webhook.site/#!/test",
        "events": ["high_risk_finding", "evidence_verified"],
        "severity_threshold": "high"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/webhooks/register",
                json=webhook_data
            ) as resp:
                result = await resp.json()
                print(f"Webhook registered: {result}")
                return True
    except Exception as e:
        print(f"Failed to register webhook: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(register_webhook())
