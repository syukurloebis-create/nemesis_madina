# scripts/architecture/interfaces/i_event_bus.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable

class IEventBus(ABC):
    """Interface for event bus"""
    
    @abstractmethod
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type"""
        pass
    
    @abstractmethod
    def get_history(self, event_type: str = None) -> List[Dict[str, Any]]:
        """Get event history"""
        pass