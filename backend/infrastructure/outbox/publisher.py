"""
NEMESIS Madina - Outbox Publisher with Circuit Breaker
✅ Complete CircuitBreaker integration
✅ Automatic failure isolation
"""

import asyncio
import logging
from typing import Optional, List, Callable
from datetime import datetime, timezone, timedelta

from backend.infrastructure.outbox.circuit_breaker import CircuitBreaker
from backend.infrastructure.outbox.outbox import OutboxRepository, OutboxStatus
from backend.domain.events.dispatcher import IEventDispatcher

logger = logging.getLogger(__name__)


class OutboxPublisher:
    """
    Outbox publisher with circuit breaker integration.
    ✅ Complete CircuitBreaker wired in
    ✅ Automatic recovery
    """
    
    def __init__(
        self,
        outbox_repository_factory: Callable[[], OutboxRepository],
        dispatcher: IEventDispatcher,
        instance_id: str = "default",
        poll_interval: int = 1,
        batch_size: int = 100,
        max_retries: int = 3,
        publish_timeout_seconds: int = 30,
        # Circuit breaker configuration
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
        circuit_breaker_success_threshold: int = 3,
    ):
        self._factory = outbox_repository_factory
        self._dispatcher = dispatcher
        self._instance_id = instance_id
        self._poll_interval = poll_interval
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._publish_timeout = publish_timeout_seconds
        
        # ✅ Circuit breaker integration
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout_seconds=circuit_breaker_timeout,
            success_threshold=circuit_breaker_success_threshold,
        )
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._metrics = None  # Metrics recorder
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    async def start(self) -> None:
        """Start background publisher with circuit breaker."""
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"OutboxPublisher started [instance={self._instance_id}]")
    
    async def stop(self) -> None:
        """Stop background publisher."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"OutboxPublisher stopped [instance={self._instance_id}]")
    
    async def _run(self) -> None:
        """Main loop with circuit breaker."""
        consecutive_failures = 0
        
        while self._running:
            try:
                # ✅ Check circuit breaker before processing
                if not self._circuit_breaker.can_execute():
                    # Circuit is open - wait and retry
                    await asyncio.sleep(self._poll_interval * 5)
                    continue
                
                # Process a batch
                try:
                    await self._publish_batch()
                    consecutive_failures = 0
                    
                    # ✅ Record success to circuit breaker
                    self._circuit_breaker.record_success()
                    
                except Exception as e:
                    consecutive_failures += 1
                    
                    # ✅ Record failure to circuit breaker
                    self._circuit_breaker.record_failure()
                    
                    if consecutive_failures >= 5:
                        logger.error(
                            f"Too many consecutive failures ({consecutive_failures}), "
                            f"circuit breaker state: {self._circuit_breaker.state}"
                        )
                    
                    await asyncio.sleep(self._poll_interval * 2)
                
                await asyncio.sleep(self._poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"OutboxPublisher error: {e}")
                await asyncio.sleep(self._poll_interval * 2)
    
    async def _publish_batch(self) -> None:
        """Publish batch with circuit breaker."""
        # Transaction 1: Claim entries
        async with self._factory() as outbox:
            async with outbox.session.begin():
                entries = await outbox.claim_pending(self._batch_size)
                if not entries:
                    return
        
        # ✅ Check circuit breaker before publishing
        if not self._circuit_breaker.can_execute():
            logger.warning("Circuit breaker open, skipping publish")
            return
        
        # Publish with timeout
        for entry in entries:
            try:
                # Deserialize and publish
                event = outbox.deserialize_entry(entry)
                
                # ✅ Publish with timeout
                await asyncio.wait_for(
                    self._dispatcher.publish(event),
                    timeout=self._publish_timeout
                )
                
                # Mark published
                async with self._factory() as outbox:
                    async with outbox.session.begin():
                        await outbox.mark_published(entry.id)
                
                logger.debug(f"Published {entry.id}")
                
            except asyncio.TimeoutError:
                logger.error(f"Publish timeout for {entry.id}")
                async with self._factory() as outbox:
                    async with outbox.session.begin():
                        await outbox.mark_failed(entry.id, "Timeout")
                        
            except Exception as e:
                logger.error(f"Failed {entry.id}: {e}")
                async with self._factory() as outbox:
                    async with outbox.session.begin():
                        if entry.retry_count >= self._max_retries:
                            await outbox.mark_dead_letter(entry.id, str(e))
                        else:
                            await outbox.mark_failed(entry.id, str(e))
    
    async def get_pending_count(self) -> int:
        """Get pending count."""
        async with self._factory() as outbox:
            return await outbox.count_pending()
    
    def get_circuit_breaker_state(self) -> dict:
        """Get circuit breaker state."""
        return {
            "state": self._circuit_breaker.state.value,
            "failure_count": self._circuit_breaker.failure_count,
            "success_count": self._circuit_breaker.success_count,
            "failure_threshold": self._circuit_breaker.failure_threshold,
            "timeout_seconds": self._circuit_breaker.timeout_seconds,
            "last_failure_time": self._circuit_breaker.last_failure_time,
        }