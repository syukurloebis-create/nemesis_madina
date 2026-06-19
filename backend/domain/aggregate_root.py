# backend/domain/aggregate_root.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional  # ← TAMBAHKAN
from datetime import datetime
import uuid


class AggregateRoot(ABC):
    """Base aggregate root with event sourcing"""
    
    def __init__(self, aggregate_id: uuid.UUID):
        self.id = aggregate_id
        self.version = 0
        self._changes: List[Dict[str, Any]] = []
        self._loaded_events: List[Dict[str, Any]] = []
    
    @abstractmethod
    def _apply_event(self, event: Dict[str, Any]):
        """Apply event to aggregate state"""
        pass
    
    def load_from_history(self, events: List[Dict[str, Any]]):
        """Load aggregate state from event history"""
        self._loaded_events = events
        for event in events:
            self._apply_event(event)
            self.version = event.get('version', self.version)
    
    def add_event(self, event_type: str, payload: Dict[str, Any], metadata: Dict[str, Any]):
        """Add new event to be saved"""
        event = {
            'aggregate_id': str(self.id),
            'event_type': event_type,
            'payload': payload,
            'metadata': metadata,
            'version': self.version + 1,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._changes.append(event)
        self._apply_event(event)
        self.version += 1
    
    def get_pending_events(self) -> List[Dict[str, Any]]:
        """Get unsaved events"""
        return self._changes
    
    def clear_pending_events(self):
        """Clear pending events after save"""
        self._changes = []
    
    @property
    def has_pending_events(self) -> bool:
        return len(self._changes) > 0