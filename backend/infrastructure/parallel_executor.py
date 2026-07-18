"""
Parallel Executor — Infrastructure-level Concurrency.

Architecture Decision:
- ParallelExecutor is infrastructure, NOT in Service
- Service calls ParallelExecutor.execute()
- Semaphore for concurrency limit
- Retry Policy for transient failures
- Circuit Breaker for cascading failures
- Timeout for each collector
- Metrics for observability
- ✅ Setiap collector mendapat UnitOfWork sendiri (tidak sharing session)
"""

import os
from dataclasses import dataclass
import asyncio
import time
from typing import List, Dict, Any, Optional, TypeVar, Generic
from enum import Enum

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork, UnitOfWorkFactory
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import (
    FraudCollectorDTO,
    GraphCollectorDTO,
    RiskCollectorDTO,
    EvidenceCollectorDTO,
    ProcurementCollectorDTO
)

import logging

logger = logging.getLogger(__name__)


# ============================================================
# RETRY POLICY & CIRCUIT BREAKER
# ============================================================

@dataclass(frozen=True)
class RetryPolicy:
    """Retry Policy for transient failures."""
    max_attempts: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 5000
    backoff_multiplier: float = 2.0
    
    @classmethod
    def default(cls) -> "RetryPolicy":
        return cls()
    
    @classmethod
    def fast(cls) -> "RetryPolicy":
        return cls(max_attempts=2, initial_delay_ms=50)
    
    @classmethod
    def resilient(cls) -> "RetryPolicy":
        return cls(max_attempts=5, initial_delay_ms=200, max_delay_ms=10000)


@dataclass
class CircuitBreaker:
    """Circuit Breaker for cascading failure prevention."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    _failure_count: int = 0
    _state: str = "closed"  # "closed", "open", "half_open"
    _last_failure_time: Optional[float] = None
    
    @classmethod
    def default(cls) -> "CircuitBreaker":
        return cls()
    
    def record_success(self) -> None:
        """Record a success."""
        if self._state == "half_open":
            self._state = "closed"
            self._failure_count = 0
        elif self._state == "closed":
            self._failure_count = max(0, self._failure_count - 1)
    
    def record_failure(self) -> None:
        """Record a failure."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == "half_open":
            self._state = "open"
        elif self._state == "closed" and self._failure_count >= self.failure_threshold:
            self._state = "open"
    
    def allow_request(self) -> bool:
        """Check if request is allowed."""
        if self._state == "closed":
            return True
        
        if self._state == "open":
            if self._last_failure_time is None:
                return False
            if time.time() - self._last_failure_time > self.timeout_seconds:
                self._state = "half_open"
                return True
            return False
        
        # half_open
        return True


# ============================================================
# COLLECTOR RESULT
# ============================================================

@dataclass
class CollectorResult:
    """Result from a single collector execution."""
    name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0
    attempts: int = 1


# ============================================================
# COLLECTOR RESULT REGISTRY
# ============================================================

@dataclass
class CollectorResultRegistry:
    """
    Collector Result Registry — Type-safe results.
    
    NOT dict[str, Any].
    Type-safe properties for each collector.
    """
    fraud: Optional[FraudCollectorDTO] = None
    graph: Optional[GraphCollectorDTO] = None
    risk: Optional[RiskCollectorDTO] = None
    evidence: Optional[EvidenceCollectorDTO] = None
    procurement: Optional[ProcurementCollectorDTO] = None
    
    def get(self, name: str):
        """Get result by name."""
        return getattr(self, name, None)
    
    def has_fraud(self) -> bool:
        return self.fraud is not None
    
    def has_graph(self) -> bool:
        return self.graph is not None
    
    def has_risk(self) -> bool:
        return self.risk is not None
    
    def has_evidence(self) -> bool:
        return self.evidence is not None
    
    def has_procurement(self) -> bool:
        return self.procurement is not None
    
    def all_present(self) -> bool:
        return all([
            self.has_fraud(),
            self.has_graph(),
            self.has_risk(),
            self.has_evidence(),
            self.has_procurement()
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dict for logging."""
        return {
            "fraud": self.fraud is not None,
            "graph": self.graph is not None,
            "risk": self.risk is not None,
            "evidence": self.evidence is not None,
            "procurement": self.procurement is not None
        }


# ============================================================
# PARALLEL EXECUTOR — with from_environment()
# ============================================================

class ParallelExecutor:
    """Parallel Executor — Infrastructure-level Concurrency."""
    
    def __init__(
        self,
        max_concurrent: int = 4,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        timeout_seconds: float = 30.0,
        enable_metrics: bool = True
    ):
        self._max_concurrent = max(1, min(max_concurrent, 64))
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
        self._retry_policy = retry_policy or RetryPolicy.default()
        self._circuit_breaker = circuit_breaker or CircuitBreaker.default()
        self._timeout_seconds = timeout_seconds
        self._enable_metrics = enable_metrics
        self._results: List[CollectorResult] = []
    
    @classmethod
    def from_environment(cls) -> "ParallelExecutor":
        """Create ParallelExecutor from environment variables."""
        max_concurrent_str = os.getenv("NEMESIS_MAX_COLLECTORS", "4")
        try:
            max_concurrent = int(max_concurrent_str)
            max_concurrent = max(1, min(max_concurrent, 64))
        except ValueError:
            max_concurrent = 4
        
        timeout_str = os.getenv("NEMESIS_COLLECTOR_TIMEOUT", "30")
        try:
            timeout_seconds = float(timeout_str)
            timeout_seconds = max(1, min(timeout_seconds, 120))
        except ValueError:
            timeout_seconds = 30
        
        return cls(max_concurrent=max_concurrent, timeout_seconds=timeout_seconds)
    
    @classmethod
    def default(cls) -> "ParallelExecutor":
        """Default ParallelExecutor."""
        return cls(max_concurrent=4, timeout_seconds=30)
    
    @classmethod
    def testing(cls) -> "ParallelExecutor":
        """Testing ParallelExecutor (faster timeouts)."""
        return cls(max_concurrent=2, timeout_seconds=5)
    
    async def execute(
        self,
        collectors: List[ICollector],
        uow_factory: UnitOfWorkFactory,
        context: ExecutionContext
    ) -> CollectorResultRegistry:
        logger.error("🚨🚨🚨 ParallelExecutor.execute() WAS CALLED! 🚨🚨🚨")
        logger.error("🚨 collectors count: %d", len(collectors))
        for c in collectors:
            logger.error("🚨 collector type: %s", type(c).__name__)
        """
        Execute all collectors in parallel with separate UoW each.

        ✅ Setiap collector mendapat UnitOfWork sendiri
        ✅ Tidak ada session sharing
        """
        self._results = []

        async def run_collector(collector: ICollector) -> CollectorResult:
            name = collector.__class__.__name__.replace("Collector", "").lower()
            # ✅ Setiap collector mendapat UoW sendiri
            async with uow_factory.create() as uow:
                # ✅ Indentasi yang benar
                return await self._execute_with_safety(collector, name, uow, context)

        tasks = [run_collector(c) for c in collectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        registry = CollectorResultRegistry()

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Collector execution failed: {result}")
                continue
            if isinstance(result, CollectorResult):
                if result.success:
                    logger.warning(
                        "🔍 Collector %s succeeded with data: %r",
                        result.name,
                        result.data
                    )
                    self._set_registry_value(registry, result.name, result.data)
                else:
                    logger.warning(f"Collector {result.name} failed: {result.error}")

        logger.warning(
            "🔍 Registry after execution: fraud=%s, graph=%s, risk=%s, evidence=%s, procurement=%s",
            registry.fraud is not None,
            registry.graph is not None,
            registry.risk is not None,
            registry.evidence is not None,
            registry.procurement is not None,
        )
    

        return registry
    
    async def _execute_with_safety(
        self,
        collector: ICollector,
        name: str,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> CollectorResult:
        """Execute a single collector with safety features."""
        start_time = time.time()
        attempts = 0
        last_error = None
        
        # Check circuit breaker
        if not self._circuit_breaker.allow_request():
            logger.warning(f"Circuit breaker open for {name}")
            return CollectorResult(
                name=name,
                success=False,
                error="Circuit breaker open",
                duration_ms=(time.time() - start_time) * 1000,
                attempts=0
            )
        
        # Retry loop
        for attempt in range(self._retry_policy.max_attempts):
            attempts = attempt + 1
            try:
                # Acquire semaphore (concurrency limit)
                async with self._semaphore:
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        collector.collect(uow, context),
                        timeout=self._timeout_seconds
                    )
                
                # Success
                self._circuit_breaker.record_success()
                duration_ms = (time.time() - start_time) * 1000
                
                logger.debug(f"Collector {name} succeeded in {duration_ms:.2f}ms (attempt {attempts})")
                
                return CollectorResult(
                    name=name,
                    success=True,
                    data=result,
                    duration_ms=duration_ms,
                    attempts=attempts
                )
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self._timeout_seconds}s"
                logger.warning(f"Collector {name} timeout (attempt {attempts})")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Collector {name} failed (attempt {attempts}): {e}")
                
                # Check if retry is appropriate
                if attempt < self._retry_policy.max_attempts - 1:
                    delay = min(
                        self._retry_policy.initial_delay_ms * (self._retry_policy.backoff_multiplier ** attempt),
                        self._retry_policy.max_delay_ms
                    ) / 1000
                    await asyncio.sleep(delay)
        
        # All attempts failed
        self._circuit_breaker.record_failure()
        duration_ms = (time.time() - start_time) * 1000
        
        logger.error(f"Collector {name} failed after {attempts} attempts: {last_error}")
        
        return CollectorResult(
            name=name,
            success=False,
            error=last_error,
            duration_ms=duration_ms,
            attempts=attempts
        )
    
    def _set_registry_value(
        self,
        registry: CollectorResultRegistry,
        name: str,
        data: Any
    ) -> None:
        """Set registry value by name."""
        if name == "fraud":
            registry.fraud = data
        elif name == "graph":
            registry.graph = data
        elif name == "risk":
            registry.risk = data
        elif name == "evidence":
            registry.evidence = data
        elif name == "procurement":
            registry.procurement = data
        else:
            logger.warning(f"Unknown collector result: {name}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        if not self._results:
            return {"total": 0}
        
        total = len(self._results)
        success = sum(1 for r in self._results if r.success)
        failed = total - success
        
        avg_duration = sum(r.duration_ms for r in self._results) / total if total > 0 else 0
        avg_attempts = sum(r.attempts for r in self._results) / total if total > 0 else 0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "avg_duration_ms": round(avg_duration, 2),
            "avg_attempts": round(avg_attempts, 2)
        }