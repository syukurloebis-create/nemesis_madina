# execution_sink_interface.py
"""
Execution Sink Interface - Abstract logging layer.
Phase 1.6 - Contract Enforcement & Abstraction
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from contracts import ArtifactEnvelope, ExecutionRecord, ArtifactId


class ExecutionSink(ABC):
    """Abstract execution sink interface."""
    
    @abstractmethod
    def log_start(self, node_name: str, execution_id: str, input_artifacts: List[ArtifactId]) -> str:
        """Log the start of execution."""
        pass
    
    @abstractmethod
    def log_completion(
        self,
        node_name: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        status: str,
        input_artifacts: List[ArtifactId],
        output_artifact: Optional[ArtifactId] = None,
        artifact_checksum: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """Log the completion of execution."""
        pass
    
    @abstractmethod
    def get_entries(self) -> List[ExecutionRecord]:
        """Get all log entries."""
        pass
    
    @abstractmethod
    def verify(self) -> bool:
        """Verify log integrity."""
        pass


class MemoryExecutionSink(ExecutionSink):
    """In-memory implementation of execution sink."""
    
    def __init__(self):
        self._entries: List[ExecutionRecord] = []
        self._sequence = 0
    
    def log_start(self, node_name: str, execution_id: str, input_artifacts: List[ArtifactId]) -> str:
        return execution_id
    
    def log_completion(
        self,
        node_name: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        status: str,
        input_artifacts: List[ArtifactId],
        output_artifact: Optional[ArtifactId] = None,
        artifact_checksum: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        from contracts import ExecutionRecord
        from datetime import datetime
        
        record = ExecutionRecord(
            node_name=node_name,
            execution_id=execution_id,
            started_at=datetime.fromisoformat(started_at),
            completed_at=datetime.fromisoformat(completed_at),
            status=status,
            input_artifacts=input_artifacts,
            output_artifact=output_artifact,
            error=error,
            retry_count=retry_count
        )
        self._entries.append(record)
        self._sequence += 1
    
    def get_entries(self) -> List[ExecutionRecord]:
        return self._entries.copy()
    
    def verify(self) -> bool:
        return True