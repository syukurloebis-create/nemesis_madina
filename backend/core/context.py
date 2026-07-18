"""
Execution Context — Immutable Metadata dengan Helper Functions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from contextvars import ContextVar

from backend.core.version import VersionInfo


# ============================================================
# REQUEST ID CONTEXT (ContextVar)
# ============================================================

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid4())


def generate_trace_id() -> str:
    """Generate a unique trace ID (eksplisit untuk tracing)."""
    return str(uuid4())


def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    _request_id_ctx.set(request_id)


def get_request_id() -> Optional[str]:
    """Get request ID from context."""
    return _request_id_ctx.get()


# ============================================================
# EXECUTION CONTEXT
# ============================================================

@dataclass(frozen=True)
class ExecutionContext:
    """
    Execution Context — Immutable Metadata.
    
    Characteristics:
    - Immutable (frozen=True)
    - VersionInfo in context (NOT in DTO)
    - with_* methods for immutable copy
    - Helper functions di level modul
    - Timestamp menggunakan UTC
    """
    
    case_id: UUID
    request_id: str = field(default_factory=generate_request_id)
    trace_id: Optional[str] = None
    version: Optional[VersionInfo] = None
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    @classmethod
    def create(
        cls,
        case_id: UUID,
        version: Optional[VersionInfo] = None,
        trace_id: Optional[str] = None
    ) -> "ExecutionContext":
        """Factory method untuk membuat context."""
        return cls(
            case_id=case_id,
            version=version or VersionInfo.default(),
            trace_id=trace_id or generate_trace_id()
        )
    
    def with_trace_id(self, trace_id: str) -> "ExecutionContext":
        """Buat copy immutable dengan trace_id yang baru."""
        return ExecutionContext(
            case_id=self.case_id,
            request_id=self.request_id,
            trace_id=trace_id,
            version=self.version,
            started_at=self.started_at
        )
    
    def with_version(self, version: VersionInfo) -> "ExecutionContext":
        """Buat copy immutable dengan version yang baru."""
        return ExecutionContext(
            case_id=self.case_id,
            request_id=self.request_id,
            trace_id=self.trace_id,
            version=version,
            started_at=self.started_at
        )
    
    def to_log_dict(self) -> dict:
        """Export to dict for logging."""
        return {
            "case_id": str(self.case_id),
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "version": self.version.to_dict() if self.version else None,
            "started_at": self.started_at.isoformat()
        }