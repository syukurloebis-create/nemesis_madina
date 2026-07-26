# tests/chaos/test_recovery.py

"""
NEMESIS Madina - Chaos Recovery Test
✅ Complete chaos testing specification
"""

import os  # ✅ Tambahkan
import asyncio
import signal
import pytest
from contextlib import suppress

# ============================================================
# MARKERS (module-level)
# ============================================================

pytestmark = [
    pytest.mark.chaos,
    pytest.mark.requires_chaos_environment,
]


# ============================================================
# TEST CODE
# ============================================================

class TestChaosRecovery:
    """Chaos recovery tests."""

    @pytest.fixture
    async def setup(self):
        """Setup chaos test environment."""
        services = await start_all_services()
        events = await generate_test_events(1000)
        yield {"services": services, "events": events}
        await stop_all_services()

    @pytest.mark.asyncio
    async def test_publisher_restart_recovery(self, setup):
        """Test publisher recovery after restart."""
        async with setup["services"]["publisher"] as publisher:
            await publisher.publish_batch(setup["events"])

        pid = setup["services"]["publisher"].pid
        os.kill(pid, signal.SIGTERM)
        await asyncio.sleep(1)

        # ✅ Restart publisher (variable removed, just start)
        await start_publisher()

        processed = await get_processed_count()
        assert processed == len(setup["events"])

        unique = await get_unique_event_count()
        assert unique == len(setup["events"])

    @pytest.mark.asyncio
    async def test_database_restart_recovery(self, setup):
        """Test recovery after database restart."""
        async with setup["services"]["uow"] as uow:
            for event in setup["events"][:100]:
                await uow.collect_event(event)

            await restart_database()

            count = await get_event_count()
            assert count == 0

        async with setup["services"]["uow"] as uow:
            for event in setup["events"]:
                await uow.collect_event(event)
            await uow.commit()

        count = await get_event_count()
        assert count == len(setup["events"])

    @pytest.mark.asyncio
    async def test_projection_crash_recovery(self, setup):
        """Test projection recovery after crash."""
        rebuilder = setup["services"]["rebuilder"]

        # ✅ Task lifecycle management
        task = asyncio.create_task(rebuilder.rebuild())
        try:
            await asyncio.sleep(2)
            await crash_projection()
            await asyncio.sleep(3)

            checkpoint = await get_checkpoint()
            assert checkpoint > 0

            await rebuilder.rebuild(resume=True)

            total = await get_projection_count()
            assert total == len(setup["events"])
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    @pytest.mark.asyncio
    async def test_network_partition_recovery(self, setup):
        """Test recovery after network partition."""
        await simulate_kafka_partition()

        async with setup["services"]["publisher"] as publisher:
            await publisher.publish_batch(setup["events"])

        circuit_state = await get_circuit_state()
        assert circuit_state == "open"

        # TODO: Replace with eventually() helper
        # See: tests/chaos/helpers/eventually.py
        await asyncio.sleep(60)
        circuit_state = await get_circuit_state()
        assert circuit_state == "half_open"

        await restore_kafka_partition()

        # TODO: Replace with eventually() helper
        await asyncio.sleep(10)

        count = await get_published_count()
        assert count == len(setup["events"])