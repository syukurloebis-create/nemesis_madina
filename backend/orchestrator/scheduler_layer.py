"""
Scheduler Layer – Controlled Execution Engine
NOW ENFORCED as MANDATORY path for ALL execution
"""

import logging
import asyncio
from typing import Optional, Callable, Awaitable
from datetime import datetime

from orchestrator.registry import ExecutionRegistry
from orchestrator.watchdog import HealthWatchdog
from orchestrator.models import ExecutionJob, JobStatus

logger = logging.getLogger(__name__)


class SchedulerLayer:
    """
    Controlled execution engine – MANDATORY path for all jobs
    
    Design rules (ENFORCED):
    - NO job execution outside this scheduler
    - Registry-driven job execution only
    - Idempotent job execution only
    - Heartbeat for watchdog monitoring
    """
    
    def __init__(self, registry: ExecutionRegistry, watchdog: HealthWatchdog):
        self.registry = registry
        self.watchdog = watchdog
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._job_queue: asyncio.Queue = asyncio.Queue()
        self._heartbeat_interval_seconds = 5
        self._poll_interval_seconds = 0.5  # Faster polling
        self._num_workers = 4
        self._worker_tasks = []
        
        # Execution handler (to be set by orchestrator)
        self._execution_handler: Optional[Callable[[ExecutionJob], Awaitable[None]]] = None
        
        logger.info("SchedulerLayer initialized")
    
    def set_execution_handler(self, handler: Callable[[ExecutionJob], Awaitable[None]]):
        """Set the actual execution function (called by orchestrator)"""
        self._execution_handler = handler
        logger.info("Execution handler registered")
    
    async def start(self):
        """Start the scheduler and worker pool"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        if not self._execution_handler:
            raise RuntimeError("Execution handler must be set before starting scheduler")
        
        self._running = True
        
        # Start scheduler loop
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start worker pool
        for i in range(self._num_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self._worker_tasks.append(task)
        
        logger.info("SchedulerLayer started with %d workers", self._num_workers)
    
    async def stop(self):
        """Stop the scheduler and workers"""
        self._running = False
        
        # Cancel scheduler
        if self._scheduler_task:
            self._scheduler_task.cancel()
            await asyncio.gather(self._scheduler_task, return_exceptions=True)
        
        # Cancel workers
        for task in self._worker_tasks:
            task.cancel()
        
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        logger.info("SchedulerLayer stopped")
    
    async def enqueue(self, job: ExecutionJob) -> bool:
        """
        ENTRY POINT – All jobs MUST go through this method
        
        This is the ONLY way to schedule a job for execution
        """
        if not self._running:
            logger.error("Scheduler not running, cannot enqueue job %s", job.job_id)
            return False
        
        # Verify job is in registry
        registered_job = self.registry.get_job(job.job_id)
        if not registered_job:
            logger.error("Job %s not found in registry – REJECTED", job.job_id)
            return False
        
        # Update status to PENDING
        self.registry.update_status(job.job_id, JobStatus.PENDING)
        
        # Add to queue
        await self._job_queue.put(job)
        logger.debug("Job %s enqueued (queue size: %d)", job.job_id, self._job_queue.qsize())
        
        return True
    
    async def _scheduler_loop(self):
        """Main scheduler loop – dispatches jobs to workers"""
        last_heartbeat = datetime.utcnow()
        
        logger.info("Scheduler loop started")
        
        while self._running:
            try:
                # Send heartbeat periodically
                now = datetime.utcnow()
                if (now - last_heartbeat).total_seconds() >= self._heartbeat_interval_seconds:
                    self.watchdog.record_scheduler_heartbeat()
                    last_heartbeat = now
                
                # Check for stuck jobs (running too long)
                await self._check_stuck_jobs()
                
                await asyncio.sleep(self._poll_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Scheduler loop error: %s", str(e))
                await asyncio.sleep(1)
        
        logger.info("Scheduler loop ended")
    
    async def _worker_loop(self, worker_id: int):
        """Worker that executes jobs from queue"""
        logger.info("Worker %d started", worker_id)
        
        while self._running:
            try:
                # Get job from queue with timeout
                job = await asyncio.wait_for(self._job_queue.get(), timeout=1.0)
                
                logger.info("Worker %d processing job %s (%s)", 
                           worker_id, job.job_id, job.event_type.value)
                
                # Execute using registered handler
                if self._execution_handler:
                    start_time = datetime.utcnow()
                    
                    try:
                        await self._execution_handler(job)
                        
                        # Record latency
                        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                        self.watchdog.record_execution_latency(latency_ms)
                        
                        logger.info("Worker %d completed job %s in %.2fms", 
                                   worker_id, job.job_id, latency_ms)
                        
                    except Exception as e:
                        logger.error("Worker %d failed job %s: %s", worker_id, job.job_id, str(e))
                        self.watchdog.record_job_failure(job.job_id, str(e))
                        
                        # Handle retry
                        if job.retry_count < job.max_retries:
                            self.registry.increment_retry(job.job_id)
                            # Re-enqueue for retry
                            await self.enqueue(job)
                        else:
                            self.registry.update_status(job.job_id, JobStatus.DEADLETTER, str(e))
                else:
                    logger.error("No execution handler for job %s", job.job_id)
                    self.registry.update_status(job.job_id, JobStatus.FAILED, "No execution handler")
                
                self._job_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker %d unexpected error: %s", worker_id, str(e))
                await asyncio.sleep(0.1)
        
        logger.info("Worker %d stopped", worker_id)
    
    async def _check_stuck_jobs(self):
        """Check for jobs that have been running too long"""
        running_jobs = self.registry.get_running_jobs()
        stuck_threshold_seconds = 300  # 5 minutes
        
        for job in running_jobs:
            age = (datetime.utcnow() - job.last_updated).total_seconds()
            if age > stuck_threshold_seconds:
                logger.warning("Job %s appears stuck (running for %.0f seconds)", 
                              job.job_id, age)
                self.watchdog.record_job_failure(job.job_id, "Job stuck")
                self.registry.update_status(job.job_id, JobStatus.RETRYING, "Job timeout")
                await self.enqueue(job)
    
    def get_queue_depth(self) -> int:
        """Get current queue depth"""
        return self._job_queue.qsize()
    
    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        return {
            "running": self._running,
            "queue_depth": self._job_queue.qsize(),
            "num_workers": self._num_workers,
            "heartbeat_interval": self._heartbeat_interval_seconds,
            "poll_interval": self._poll_interval_seconds,
            "has_handler": self._execution_handler is not None
        }