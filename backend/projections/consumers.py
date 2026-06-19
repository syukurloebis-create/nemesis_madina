import asyncio
import json
from typing import Optional, Callable, Awaitable
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext

class EventConsumer:
    """NATS JetStream consumer untuk event processing."""

    def __init__(self, nc: NATS, js: JetStreamContext):
        self.nc = nc
        self.js = js
        self._subscriptions = []

    async def subscribe(self, subject: str, handler: Callable[[dict], Awaitable[None]],
                        durable: str = None, queue: str = None):
        """Subscribe ke subject dengan durable consumer."""

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await handler(data)
                await msg.ack()
            except Exception as e:
                print(f"❌ Consumer error: {e}")
                await msg.nak()

        sub = await self.js.subscribe(
            subject,
            cb=message_handler,
            durable=durable,
            queue=queue,
            manual_ack=True
        )
        self._subscriptions.append(sub)
        print(f"✅ Subscribed to {subject} (durable={durable})")
        return sub

    async def close(self):
        for sub in self._subscriptions:
            await sub.unsubscribe()
        self._subscriptions.clear()
