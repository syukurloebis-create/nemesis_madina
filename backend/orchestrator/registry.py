"""
Execution Registry – Source of Truth untuk semua jobs
P1 Priority – Idempotency enforcement center
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from uuid import uuid4

from backend.orchestrator.models import ExecutionJob, JobStatus, EventType

logger = logging.getLogger(__name__)


class ExecutionRegistry:
    """
    Global job registry – memastikan idempotency dan tracking lifecycle
    
    Design rules:
    - No duplicate job with same idempotency_key ever allowed
    - All executions must be registered first
    - Complete audit trail of job lifecycle
    """
    
    def __init__(self, ttl_minutes: int = 60 * 24 * 7):  # 7 days default
        self._jobs: Dict[str, ExecutionJob] = {}  # job_id -> job
        self._idempotency_map: Dict[str, str] = {}  # idempotency_key -> job_id
        self._history: Dict[str, List[ExecutionJob]] = defaultdict(list)
        self.ttl = timedelta(minutes=ttl_minutes)
        logger.info("ExecutionRegistry initialized with TTL %s", self.ttl)
    
    def register(self, event: dict) -> ExecutionJob:
        """
        Register new execution job
        
        Critical: Idempotency check BEFORE any execution
        """
        # Extract idempotency key
        idempotency_key = event.get("idempotency_key") or event.get("event_id")
        
        if not idempotency_key:
            # Generate if not provided (but better to require)
            idempotency_key = f"{event.get('event_type', 'unknown')}_{datetime.utcnow().timestamp()}"
            logger.warning("No idempotency_key provided, generated: %s", idempotency_key)
        
        # IDEMPOTENCY CHECK – most critical guard
        existing_job_id = self._idempotency_map.get(idempotency_key)
        if existing_job_id:
            existing_job = self._jobs.get(existing_job_id)
            if existing_job:
                logger.warning(
                    "Duplicate execution blocked! Idempotency key: %s, existing job: %s",
                    idempotency_key, existing_job.job_id
                )
                return existing_job
        
        # Get event type
        event_type_str = event.get("event_type", "TRUST_MUTATION")
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            logger.warning("Unknown event type: %s, using TRUST_MUTATION", event_type_str)
            event_type = EventType.TRUST_MUTATION
        
        # Generate correlation_id if not provided
        correlation_id = event.get("correlation_id", str(uuid4()))
        
        # Create new job (FIXED: job.correlation_id not referenced before definition)
        job = ExecutionJob(
            idempotency_key=idempotency_key,
            event_id=event.get("event_id"),
            event_type=event_type,
            payload=event.get("payload", {}),
            correlation_id=correlation_id
        )
        
        # Store
        self._jobs[job.job_id] = job
        self._idempotency_map[idempotency_key] = job.job_id
        
        logger.info("Registered new job: %s (type: %s, idempotency: %s)", 
                   job.job_id, job.event_type.value, idempotency_key)
        
        return job
    
    def get_job(self, job_id: str) -> Optional[ExecutionJob]:
        """Retrieve job by ID"""
        return self._jobs.get(job_id)
    
    def get_job_by_idempotency(self, idempotency_key: str) -> Optional[ExecutionJob]:
        """Retrieve job by idempotency key"""
        job_id = self._idempotency_map.get(idempotency_key)
        if job_id:
            return self._jobs.get(job_id)
        return None
    
    def update_status(self, job_id: str, status: JobStatus, error_message: str = None) -> bool:
        """
        Update job status with audit trail
        
        Returns: True if updated successfully
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.error("Job not found for status update: %s", job_id)
            return False
        
        # Archive to history before update (copy job state)
        import copy
        self._history[job_id].append(copy.deepcopy(job))
        
        # Update
        old_status = job.status
        job.status = status
        job.last_updated = datetime.utcnow()
        
        if status == JobStatus.COMPLETED:
            job.completed_at = datetime.utcnow()
        
        if error_message:
            job.error_message = error_message
        
        if status == JobStatus.RETRYING:
            job.retry_count += 1
        
        logger.info("Job %s status: %s -> %s", job_id, old_status.value, status.value)
        
        # Cleanup completed jobs if needed
        if status in [JobStatus.COMPLETED, JobStatus.DEADLETTER]:
            self._cleanup_if_expired(job_id)
        
        return True
    
    def increment_retry(self, job_id: str) -> bool:
        """Increment retry counter and mark for retry"""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.retry_count >= job.max_retries:
            self.update_status(job_id, JobStatus.DEADLETTER, "Max retries exceeded")
            return False
        
        self.update_status(job_id, JobStatus.RETRYING)
        return True
    
    def get_pending_jobs(self, limit: int = 100) -> List[ExecutionJob]:
        """Get all pending jobs for scheduler"""
        pending = [
            job for job in self._jobs.values()
            if job.status in [JobStatus.PENDING, JobStatus.RETRYING]
        ]
        # Sort by created_at (oldest first)
        pending.sort(key=lambda j: j.created_at)
        return pending[:limit]
    
    def get_running_jobs(self) -> List[ExecutionJob]:
        """Get currently running jobs"""
        return [
            job for job in self._jobs.values()
            if job.status == JobStatus.RUNNING
        ]
    
    def get_stats(self) -> dict:
        """Get registry statistics"""
        stats = defaultdict(int)
        for job in self._jobs.values():
            stats[job.status.value] += 1
        
        return {
            "total_jobs": len(self._jobs),
            "by_status": dict(stats),
            "unique_idempotency_keys": len(self._idempotency_map),
            "history_size": sum(len(h) for h in self._history.values())
        }
    
    def _cleanup_if_expired(self, job_id: str):
        """Cleanup completed job if expired"""
        job = self._jobs.get(job_id)
        if job and job.completed_at:
            age = datetime.utcnow() - job.completed_at
            if age > self.ttl:
                del self._jobs[job_id]
                # Remove from idempotency map
                for key, jid in list(self._idempotency_map.items()):
                    if jid == job_id:
                        del self._idempotency_map[key]
                logger.debug("Cleaned up expired job: %s", job_id)
    
    def clear_completed(self, older_than_minutes: int = 60 * 24):
        """Manual cleanup of completed jobs"""
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        to_remove = []
        
        for job_id, job in self._jobs.items():
            if job.completed_at and job.completed_at < cutoff:
                to_remove.append(job_id)
        
        for job_id in to_remove:
            del self._jobs[job_id]
            for key, jid in list(self._idempotency_map.items()):
                if jid == job_id:
                    del self._idempotency_map[key]
        
        logger.info("Cleaned up %d completed jobs", len(to_remove))
        return len(to_remove)