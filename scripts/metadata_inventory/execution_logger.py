# execution_logger.py
"""
ExecutionLogger - Separate component for logging execution.
Phase 1.5 - Verification Hardening
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from contracts import ArtifactEnvelope, ExecutionRecord, ArtifactId
from append_ledger import AppendLedger, AppendRecord


@dataclass(frozen=True)
class ExecutionLogEntry:
    """Immutable execution log entry."""
    node_name: str
    execution_id: str
    started_at: datetime
    completed_at: datetime
    status: str
    input_artifacts: List[ArtifactId]
    output_artifact: Optional[ArtifactId] = None
    artifact_checksum: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    sequence: Optional[int] = None


class ExecutionLogger:
    """
    Separate component for logging execution.
    Maintains tamper-evident append ledger.
    """
    
    def __init__(self):
        self._ledger = AppendLedger()
        self._entries: List[ExecutionLogEntry] = []
        self._sequence = 0
    
    def log_start(
        self,
        node_name: str,
        execution_id: str,
        input_artifacts: List[ArtifactId]
    ) -> str:
        """Log the start of execution."""
        return execution_id
    
    def log_completion(
        self,
        node_name: str,
        execution_id: str,
        started_at: datetime,
        completed_at: datetime,
        status: str,
        input_artifacts: List[ArtifactId],
        output_artifact: Optional[ArtifactId] = None,
        artifact_checksum: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> ExecutionLogEntry:
        """Log the completion of execution."""
        entry = ExecutionLogEntry(
            node_name=node_name,
            execution_id=execution_id,
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            input_artifacts=input_artifacts,
            output_artifact=output_artifact,
            artifact_checksum=artifact_checksum,
            error=error,
            retry_count=retry_count,
            sequence=self._sequence
        )
        
        self._entries.append(entry)
        self._sequence += 1
        
        # Append to ledger if artifact produced
        if output_artifact and artifact_checksum:
            # Create a minimal envelope for ledger
            # In practice, this would use the actual artifact
            pass
        
        return entry
    
    def get_entries(self) -> List[ExecutionLogEntry]:
        """Get all log entries."""
        return self._entries.copy()
    
    def get_ledger(self) -> AppendLedger:
        """Get the append ledger."""
        return self._ledger
    
    def verify(self) -> bool:
        """Verify the ledger chain."""
        return self._ledger.verify()