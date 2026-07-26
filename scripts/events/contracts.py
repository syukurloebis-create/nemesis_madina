# scripts/events/contracts.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

class IEvent(ABC):
    """Base interface for all events"""
    @property
    def event_id(self) -> str:
        pass
    
    @property
    def timestamp(self) -> datetime:
        pass
    
    @property
    def event_type(self) -> str:
        pass
    
    @property
    def payload(self) -> Dict[str, Any]:
        pass

@dataclass
class BaseEvent(IEvent):
    """Base event implementation"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def event_type(self) -> str:
        return self.__class__.__name__
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'data': self.to_dict()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_') and k not in ['event_id', 'timestamp']}

# Pipeline Events
@dataclass
class PipelineStartedEvent(BaseEvent):
    pipeline_id: str
    stages: list
    start_time: datetime = field(default_factory=datetime.now)

@dataclass
class PipelineCompletedEvent(BaseEvent):
    pipeline_id: str
    duration: float
    metrics: Dict[str, Any]

@dataclass
class PipelineFailedEvent(BaseEvent):
    pipeline_id: str
    error: str
    stage: str
    retry_count: int = 0

# Scanner Events
@dataclass
class ScanStartedEvent(BaseEvent):
    scanner_version: str
    root_path: str
    plugins: list

@dataclass
class ScanCompletedEvent(BaseEvent):
    scanner_version: str
    total_files: int
    total_modules: int
    total_relations: int
    duration: float

@dataclass
class ScanFailedEvent(BaseEvent):
    scanner_version: str
    error: str
    file: Optional[str] = None

# Rule Events
@dataclass
class RuleEvaluationStartedEvent(BaseEvent):
    rules_version: str
    rule_count: int
    categories: list

@dataclass
class RuleEvaluationCompletedEvent(BaseEvent):
    rules_version: str
    total_violations: int
    violations_by_severity: Dict[str, int]

@dataclass
class ViolationDetectedEvent(BaseEvent):
    rule_id: str
    message: str
    severity: str
    module: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Generator Events
@dataclass
class GenerationStartedEvent(BaseEvent):
    generator_name: str
    artifact_type: str

@dataclass
class GenerationCompletedEvent(BaseEvent):
    generator_name: str
    artifact_path: str
    artifact_size: int
    checksum: str
    duration: float

# Gate Events
@dataclass
class GateCheckStartedEvent(BaseEvent):
    pipeline_id: str
    threshold: str

@dataclass
class GateCheckPassedEvent(BaseEvent):
    pipeline_id: str
    violations_cleared: int

@dataclass
class GateCheckFailedEvent(BaseEvent):
    pipeline_id: str
    violations: list
    threshold: str