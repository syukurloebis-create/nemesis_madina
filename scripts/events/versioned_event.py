# scripts/events/versioned_event.py
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class VersionedEvent(IEvent):
    """Base class for versioned events"""
    event_version: int = 1
    schema_version: int = 1
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'event_version': self.event_version,
            'schema_version': self.schema_version,
            'data': self.to_dict()
        }

# Example: ScanCompletedEvent v1
@dataclass
class ScanCompletedEventV1(VersionedEvent):
    event_version: int = 1
    scanner_version: str = ""
    total_files: int = 0
    duration: float = 0.0

# Example: ScanCompletedEvent v2 (added metrics)
@dataclass
class ScanCompletedEventV2(VersionedEvent):
    event_version: int = 2
    scanner_version: str = ""
    total_files: int = 0
    total_modules: int = 0  # NEW
    total_relations: int = 0  # NEW
    duration: float = 0.0
    metrics: Dict[str, Any] = None  # NEW

# Event Version Mapper
class EventVersionMapper:
    """Map events between versions"""
    
    @staticmethod
    def v1_to_v2(v1_event: ScanCompletedEventV1) -> ScanCompletedEventV2:
        """Upgrade from v1 to v2"""
        return ScanCompletedEventV2(
            event_id=v1_event.event_id,
            timestamp=v1_event.timestamp,
            scanner_version=v1_event.scanner_version,
            total_files=v1_event.total_files,
            total_modules=0,  # Default
            total_relations=0,  # Default
            duration=v1_event.duration,
            metrics={}
        )
    
    @staticmethod
    def v2_to_v1(v2_event: ScanCompletedEventV2) -> ScanCompletedEventV1:
        """Downgrade from v2 to v1 (lossy)"""
        return ScanCompletedEventV1(
            event_id=v2_event.event_id,
            timestamp=v2_event.timestamp,
            scanner_version=v2_event.scanner_version,
            total_files=v2_event.total_files,
            duration=v2_event.duration
        )