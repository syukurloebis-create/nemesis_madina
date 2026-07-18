"""
NEMESIS Madina - Bounded Concurrent Publisher
✅ Concurrent publishing with concurrency control
✅ Ordering preservation when needed
"""

import asyncio
from typing import List, Optional, Callable
from dataclasses import dataclass


@dataclass
class PublishBatch:
    entries: List[OutboxEntry]
    preserve_order: bool = False


class BoundedConcurrentPublisher:
    """
    Concurrent publisher with bounded concurrency.
    ✅ Semaphore-based concurrency control
    ✅ Optional ordering preservation
    """
    
    def __init__(
        self,
        max_concurrency: int = 20,
        batch_size: int = 100,
        preserve_order: bool = False,
    ):
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._batch_size = batch_size
        self._preserve_order = preserve_order
    
    async def publish(
        self,
        entries: List[OutboxEntry],
        publish_fn: Callable[[OutboxEntry], Awaitable[None]],
    ) -> List[bool]:
        """
        Publish entries concurrently.
        ✅ Bounded by semaphore
        ✅ Returns success/failure per entry
        """
        results = [False] * len(entries)
        
        async def publish_with_semaphore(idx: int, entry: OutboxEntry) -> None:
            async with self._semaphore:
                try:
                    await publish_fn(entry)
                    results[idx] = True
                except Exception as e:
                    logger.error(f"Failed to publish {entry.id}: {e}")
                    results[idx] = False
        
        # Create tasks
        tasks = []
        for i, entry in enumerate(entries):
            tasks.append(publish_with_semaphore(i, entry))
        
        # Execute with concurrency control
        if self._preserve_order:
            # Sequential but bounded (maintains order)
            for task in tasks:
                await task
        else:
            # Concurrent (best effort)
            await asyncio.gather(*tasks)
        
        return results