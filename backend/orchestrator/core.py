"""
Nemesis Orchestrator – Single Control Plane Core
P0 Priority – Entry point untuk SEMUA execution
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Tuple  # <-- ADD THIS IMPORT
from datetime import datetime

from orchestrator.registry import ExecutionRegistry
from orchestrator.watchdog import HealthWatchdog
from core.events.bus import EventBusV2, RoutingDecision
from orchestrator.scheduler_layer import SchedulerLayer
from orchestrator.models import ExecutionJob, JobStatus, ReplayResult, HealthReport, EventType

logger = logging.getLogger(__name__)


class NemesisOrchestrator:
    """
    SINGLE CONTROL PLANE untuk NEMESIS V8+
    
    Design rules (enforced):
    1. Tidak ada execution path di luar orchestrator
    2. Semua event harus lewat orchestrator
    3. Semua execution harus terdaftar dulu di registry
    4. Idempotency enforced globally
    
    This is the ONLY entry point for:
    - New events
    - Replay operations
    - System health queries
    """
    
    def __init__(self):
        self.registry = ExecutionRegistry()
        self.watchdog = HealthWatchdog()
        self.event_bus = EventBusV2()
        self.scheduler = SchedulerLayer(self.registry, self.watchdog)
        
        # Connect scheduler to execution handler
        self.scheduler.set_execution_handler(self._execute_job)
        
        self._running = False
        
        logger.info("NemesisOrchestrator initialized – Control Plane ACTIVE")
    
    async def start(self, num_workers: int = 4):
        """Start orchestrator with worker pool"""
        self._running = True
        
        # Start scheduler (which starts its own workers)
        await self.scheduler.start()
        
        logger.info("Orchestrator started with scheduler")
    
    async def stop(self):
        """Graceful shutdown"""
        self._running = False
        
        # Stop scheduler
        await self.scheduler.stop()
        
        logger.info("Orchestrator stopped")
    
    async def submit(self, event: Dict[str, Any]) -> ExecutionJob:
        """
        Submit new event for execution
        
        This is the ONLY entry point for new events.
        """
        logger.info("Submitting event: %s", event.get("event_type", "unknown"))
        
        # STEP 1: Register with idempotency check
        job = self.registry.register(event)
        
        # If already exists and completed, return existing
        if job.status == JobStatus.COMPLETED:
            logger.info("Returning completed job: %s", job.job_id)
            return job
        
        # STEP 2: Route via event bus
        routing = self.event_bus.route(job)
        
        # STEP 3: ENFORCE – ALL jobs go through scheduler
        enqueued = await self.scheduler.enqueue(job)
        
        if not enqueued:
            logger.error("Failed to enqueue job %s", job.job_id)
            self.registry.update_status(job.job_id, JobStatus.FAILED, "Scheduler rejected")
            return job
        
        logger.info("Event submitted: job_id=%s, routing=%s", job.job_id, routing.value)
        return job
    
    async def replay(self, event_range: Tuple[str, str], entity_id: Optional[str] = None) -> ReplayResult:
        """
        Controlled replay via orchestrator
        
        Args:
            event_range: (start_event_id, end_event_id) or (start_time, end_time)
            entity_id: Optional entity filter
        """
        start_time = datetime.utcnow()
        logger.info("Starting replay: range=%s, entity=%s", event_range, entity_id)
        
        try:
            # TODO: Implement actual replay logic using existing ReplayEngine
            from core.events.replay_engine import ReplayEngine
            replay_engine = ReplayEngine()
            
            # Register replay as a job first
            replay_event = {
                "event_type": "REPLAY",
                "payload": {
                    "event_range": event_range,
                    "entity_id": entity_id
                },
                "idempotency_key": f"replay_{start_time.timestamp()}"
            }
            
            replay_job = self.registry.register(replay_event)
            
            # Execute replay
            result = await replay_engine.replay_events(
                start_id=event_range[0],
                end_id=event_range[1],
                entity_id=entity_id
            )
            
            # Update job status
            self.registry.update_status(replay_job.job_id, JobStatus.COMPLETED)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ReplayResult(
                success=True,
                total_events=result.get("total", 0),
                processed_events=result.get("processed", 0),
                failed_events=result.get("failed", 0),
                duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error("Replay failed: %s", str(e))
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return ReplayResult(
                success=False,
                total_events=0,
                processed_events=0,
                failed_events=1,
                duration_ms=duration_ms,
                errors=[str(e)]
            )
    
    async def health(self) -> HealthReport:
        """Get system health status"""
        registry_stats = self.registry.get_stats()
        return await self.watchdog.report(registry_stats)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status by ID"""
        job = self.registry.get_job(job_id)
        if job:
            return job.to_dict()
        return None
    
    async def get_job_by_idempotency(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Get job by idempotency key"""
        job = self.registry.get_job_by_idempotency(idempotency_key)
        if job:
            return job.to_dict()
        return None
    
    async def _execute_job(self, job: ExecutionJob):
        """Execute a single job (internal) – called by scheduler worker"""
        start_time = datetime.utcnow()
        self.registry.update_status(job.job_id, JobStatus.RUNNING)
        
        try:
            # Route to appropriate handler based on event type
            if job.event_type == EventType.TRUST_MUTATION:
                await self._handle_trust_mutation(job)
            elif job.event_type == EventType.RISK_UPDATE:
                await self._handle_risk_update(job)
            elif job.event_type == EventType.ANOMALY_DETECTION:
                await self._handle_anomaly(job)
            elif job.event_type == EventType.SCORE_REFRESH:
                await self._handle_score_refresh(job)
            else:
                await self._handle_default(job)
            
            # Mark as completed
            self.registry.update_status(job.job_id, JobStatus.COMPLETED)
            
            # Record latency
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.watchdog.record_execution_latency(latency_ms)
            
            logger.info("Job %s completed in %.2fms", job.job_id, latency_ms)
            
        except Exception as e:
            logger.error("Job %s failed: %s", job.job_id, str(e))
            self.watchdog.record_job_failure(job.job_id, str(e))
            raise  # Re-raise so scheduler handles retry
    
    async def _handle_trust_mutation(self, job: ExecutionJob):
        """Handle trust mutation event"""
        # TODO: Integrate with existing trust engine
        logger.debug("Handling trust mutation for job %s", job.job_id)
        # from intelligence.core.trust_model import TrustModel
        # trust_model = TrustModel()
        # ... implementation
    
    async def _handle_risk_update(self, job: ExecutionJob):
        """Handle risk update event"""
        logger.debug("Handling risk update for job %s", job.job_id)
        # TODO: Integrate with existing risk engine
        pass
    
    async def _handle_anomaly(self, job: ExecutionJob):
        """Handle anomaly detection event"""
        logger.debug("Handling anomaly detection for job %s", job.job_id)
        # TODO: Integrate with anomaly engine
        pass
    
    async def _handle_score_refresh(self, job: ExecutionJob):
        """Handle score refresh event"""
        logger.debug("Handling score refresh for job %s", job.job_id)
        # TODO: Trigger score recalculation
        pass
    
    async def _handle_default(self, job: ExecutionJob):
        """Default handler for unhandled event types"""
        logger.warning("No specific handler for event type: %s, using default", job.event_type)
        # Default: just log and succeed
        await asyncio.sleep(0.01)  # Simulate work
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "registry": self.registry.get_stats(),
            "event_bus": self.event_bus.get_stats(),
            "scheduler": self.scheduler.get_stats(),
            "running": self._running
        }