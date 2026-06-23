"""
Health Watchdog – System liveness monitoring
P2 Priority – Heartbeat, failure detection, self-awareness
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import deque

from orchestrator.models import HealthReport

logger = logging.getLogger(__name__)


class HealthWatchdog:
    """
    System health monitoring dengan heartbeat detection
    
    Responsibilities:
    - Detect stuck jobs
    - Detect scheduler deadlock
    - Detect outbox lag
    - Ensure system liveliness
    """
    
    def __init__(self):
        self._last_scheduler_heartbeat: Optional[datetime] = None
        self._heartbeat_history: deque = deque(maxlen=100)  # Last 100 heartbeats
        self._failed_jobs_history: deque = deque(maxlen=1000)
        self._execution_latencies: deque = deque(maxlen=1000)
        
        # Thresholds
        self.scheduler_timeout_seconds = 30
        self.max_worker_lag_seconds = 60
        self.max_failed_job_rate = 0.10  # 10% failure rate threshold
        
        logger.info("HealthWatchdog initialized")
    
    def record_scheduler_heartbeat(self):
        """Called periodically by scheduler to signal liveness"""
        self._last_scheduler_heartbeat = datetime.utcnow()
        self._heartbeat_history.append(self._last_scheduler_heartbeat)
        logger.debug("Scheduler heartbeat recorded")
    
    def record_job_failure(self, job_id: str, error: str):
        """Record job failure for rate calculation"""
        self._failed_jobs_history.append({
            "job_id": job_id,
            "error": error,
            "timestamp": datetime.utcnow()
        })
    
    def record_execution_latency(self, latency_ms: float):
        """Record job execution latency for p95 calculation"""
        self._execution_latencies.append(latency_ms)
    
    def is_scheduler_alive(self) -> bool:
        """Check if scheduler is still alive"""
        if not self._last_scheduler_heartbeat:
            return False
        
        age = datetime.utcnow() - self._last_scheduler_heartbeat
        return age.total_seconds() < self.scheduler_timeout_seconds
    
    def get_failed_job_rate(self, window_minutes: int = 5) -> float:
        """Calculate failed job rate in last N minutes"""
        if not self._failed_jobs_history:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_failures = sum(
            1 for f in self._failed_jobs_history
            if f["timestamp"] > cutoff
        )
        
        # Total jobs in window (estimated from registry)
        total_jobs = len(self._failed_jobs_history)  # Approximation
        
        if total_jobs == 0:
            return 0.0
        
        return recent_failures / total_jobs
    
    def get_p95_latency(self) -> float:
        """Calculate p95 execution latency in milliseconds"""
        if not self._execution_latencies:
            return 0.0
        
        sorted_latencies = sorted(self._execution_latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]
    
    async def check_outbox_lag(self) -> int:
        """
        Check outbox queue depth
        Implement based on your outbox mechanism
        """
        # TODO: Integrate dengan actual outbox
        # Contoh: return await redis.llen("outbox_queue")
        return 0
    
    async def check_worker_lag(self) -> float:
        """
        Check worker processing lag in seconds
        """
        # TODO: Implement based on worker monitoring
        return 0.0
    
    async def report(self, registry_stats: Optional[Dict] = None) -> HealthReport:
        """
        Generate comprehensive health report
        """
        scheduler_alive = self.is_scheduler_alive()
        failed_job_rate = self.get_failed_job_rate()
        p95_latency = self.get_p95_latency()
        outbox_depth = await self.check_outbox_lag()
        worker_lag = await self.check_worker_lag()
        
        # Determine overall health
        is_healthy = (
            scheduler_alive and
            worker_lag < self.max_worker_lag_seconds and
            failed_job_rate < self.max_failed_job_rate
        )
        
        # Get registry stats if provided
        pending_jobs = registry_stats.get("by_status", {}).get("PENDING", 0) if registry_stats else 0
        running_jobs = registry_stats.get("by_status", {}).get("RUNNING", 0) if registry_stats else 0
        deadletter_jobs = registry_stats.get("by_status", {}).get("DEADLETTER", 0) if registry_stats else 0
        
        return HealthReport(
            is_healthy=is_healthy,
            scheduler_alive=scheduler_alive,
            worker_lag_seconds=worker_lag,
            outbox_queue_depth=outbox_depth,
            failed_job_rate=round(failed_job_rate, 4),
            execution_latency_p95=round(p95_latency, 2),
            pending_jobs=pending_jobs,
            running_jobs=running_jobs,
            deadletter_jobs=deadletter_jobs,
            last_heartbeat=self._last_scheduler_heartbeat,
            components={
                "orchestrator": True,
                "registry": True,
                "watchdog": True,
                "scheduler": scheduler_alive,
                "outbox": outbox_depth < 1000,  # Arbitrary threshold
            }
        )
    
    async def wait_for_health(self, timeout_seconds: int = 30) -> bool:
        """
        Wait until system is healthy or timeout
        """
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < timeout_seconds:
            report = await self.report()
            if report.is_healthy:
                return True
            await asyncio.sleep(1)
        
        return False
    
    def get_heartbeat_stats(self) -> Dict[str, Any]:
        """Get heartbeat statistics"""
        if not self._heartbeat_history:
            return {"heartbeat_count": 0, "last_heartbeat": None}
        
        intervals = []
        prev = None
        for hb in self._heartbeat_history:
            if prev:
                intervals.append((hb - prev).total_seconds())
            prev = hb
        
        return {
            "heartbeat_count": len(self._heartbeat_history),
            "last_heartbeat": self._last_scheduler_heartbeat.isoformat() if self._last_scheduler_heartbeat else None,
            "avg_interval_seconds": sum(intervals) / len(intervals) if intervals else 0,
            "max_interval_seconds": max(intervals) if intervals else 0
        }