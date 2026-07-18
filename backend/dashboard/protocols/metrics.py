# backend/dashboard/protocols/metrics.py

from typing import Protocol, Optional, Dict, Any
from datetime import datetime


class MetricsRecorder(Protocol):
    """Protocol for metrics recording."""
    
    def record_execution(
        self,
        name: str,
        duration_ms: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record execution metrics."""
        ...
    
    def record_pipeline(
        self,
        name: str,
        duration_ms: float,
        success: bool
    ) -> None:
        """Record pipeline metrics."""
        ...
    
    def record_timeout(
        self,
        name: str
    ) -> None:
        """Record timeout metrics."""
        ...


class NoOpMetricsRecorder:
    """No-op metrics recorder."""
    
    def record_execution(self, name: str, duration_ms: float, success: bool, **kwargs) -> None:
        pass
    
    def record_pipeline(self, name: str, duration_ms: float, success: bool) -> None:
        pass
    
    def record_timeout(self, name: str) -> None:
        pass


class ConsoleMetricsRecorder:
    """Console metrics recorder for debugging."""
    
    def __init__(self):
        self._executions = []
    
    def record_execution(self, name: str, duration_ms: float, success: bool, **kwargs) -> None:
        print(f"📊 Execution: {name} | {duration_ms:.2f}ms | {'✅' if success else '❌'}")
        self._executions.append({
            'name': name,
            'duration_ms': duration_ms,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_pipeline(self, name: str, duration_ms: float, success: bool) -> None:
        print(f"📊 Pipeline: {name} | {duration_ms:.2f}ms | {'✅' if success else '❌'}")
    
    def record_timeout(self, name: str) -> None:
        print(f"⏰ Timeout: {name}")
    
    def get_executions(self):
        return self._executions