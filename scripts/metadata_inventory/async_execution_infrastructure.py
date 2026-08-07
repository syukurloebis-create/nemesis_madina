# async_execution_infrastructure.py
"""
Async Execution Infrastructure - Async sinks, error categories, ledger root.
Phase 1.7 - Runtime Determinism & Contract Completeness
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import hashlib
from datetime import datetime

from canonical_serializer import CanonicalSerializer


class ErrorCategory(Enum):
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    AUTH = "auth"
    RESOURCE = "resource"
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RetryableError(Exception):
    """Error that can be retried."""
    category: ErrorCategory
    message: str
    retry_after: Optional[float] = None


@dataclass(frozen=True)
class PermanentError(Exception):
    """Error that should not be retried."""
    category: ErrorCategory
    message: str


class AsyncExecutionSink:
    """Async execution sink interface."""
    
    async def log_start(
        self,
        node_name: str,
        execution_id: str,
        input_artifacts: List[str]
    ) -> None:
        """Log start of execution."""
        pass
    
    async def log_completion(
        self,
        node_name: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        status: str,
        input_artifacts: List[str],
        output_artifact: Optional[str] = None,
        artifact_checksum: Optional[str] = None,
        error: Optional[str] = None,
        error_category: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """Log completion of execution."""
        pass


class AsyncMemoryExecutionSink(AsyncExecutionSink):
    """Async in-memory execution sink."""
    
    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._sequence = 0
    
    async def log_start(
        self,
        node_name: str,
        execution_id: str,
        input_artifacts: List[str]
    ) -> None:
        self._entries.append({
            "type": "start",
            "node_name": node_name,
            "execution_id": execution_id,
            "input_artifacts": input_artifacts,
            "timestamp": datetime.now().isoformat(),
            "sequence": self._sequence
        })
        self._sequence += 1
    
    async def log_completion(
        self,
        node_name: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        status: str,
        input_artifacts: List[str],
        output_artifact: Optional[str] = None,
        artifact_checksum: Optional[str] = None,
        error: Optional[str] = None,
        error_category: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        self._entries.append({
            "type": "completion",
            "node_name": node_name,
            "execution_id": execution_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "status": status,
            "input_artifacts": input_artifacts,
            "output_artifact": output_artifact,
            "artifact_checksum": artifact_checksum,
            "error": error,
            "error_category": error_category,
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
            "sequence": self._sequence
        })
        self._sequence += 1
    
    def get_entries(self) -> List[Dict[str, Any]]:
        return self._entries.copy()


class MerkleLedger:
    """
    Merkle ledger with root hash for cross-system verification.
    """
    
    def __init__(self):
        self._records: List[Dict[str, Any]] = []
        self._root_hash: Optional[str] = None
    
    def append(self, record: Dict[str, Any]) -> str:
        """Append a record and update root hash."""
        # Calculate record hash
        record_hash = hashlib.sha256(
            CanonicalSerializer.serialize(record).encode()
        ).hexdigest()[:16]
        
        # Add hash to record
        record_with_hash = {**record, "record_hash": record_hash}
        self._records.append(record_with_hash)
        
        # Update root hash
        self._root_hash = self._calculate_root_hash()
        
        return record_hash
    
    def _calculate_root_hash(self) -> str:
        """Calculate Merkle root hash."""
        if not self._records:
            return "0" * 64
        
        # Get all record hashes
        hashes = [r["record_hash"] for r in self._records]
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
                new_hashes.append(new_hash)
            hashes = new_hashes
        
        return hashes[0] if hashes else "0" * 64
    
    def get_root_hash(self) -> str:
        """Get current Merkle root hash."""
        if self._root_hash is None:
            self._root_hash = self._calculate_root_hash()
        return self._root_hash
    
    def verify(self) -> bool:
        """Verify ledger integrity."""
        expected_root = self._calculate_root_hash()
        return expected_root == self._root_hash
    
    def get_records(self) -> List[Dict[str, Any]]:
        return self._records.copy()