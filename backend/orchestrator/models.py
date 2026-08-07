"""
Orchestrator Models
===================

Domain models for the orchestrator.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    DASHBOARD_GENERATED = "dashboard_generated"
    COLLECTOR_COMPLETED = "collector_completed"
    COLLECTOR_FAILED = "collector_failed"
    GRAPH_UPDATED = "graph_updated"
    RISK_ASSESSMENT_COMPLETED = "risk_assessment_completed"


@dataclass
class ExecutionJob:
    job_id: str
    event_type: EventType
    payload: dict
    status: JobStatus = JobStatus.PENDING
    case_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class HealthReport:
    status: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    components: Dict[str, str] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayResult:
    """Result of replaying a dead letter event."""
    success: bool
    message: str
    event_id: Optional[str] = None
    replayed_at: datetime = field(default_factory=datetime.utcnow)