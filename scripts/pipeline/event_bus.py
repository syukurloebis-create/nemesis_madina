# scripts/pipeline/event_bus.py
from typing import Callable, Dict, List, Type
from scripts.events.contracts import IEvent

class GovernanceEventBus:
    def __init__(self):
        self.subscribers: Dict[Type[IEvent], List[Callable]] = {}
        self.event_history: List[IEvent] = []
    
    def publish(self, event: IEvent):
        """Publish a typed event"""
        self.event_history.append(event)
        
        event_type = type(event)
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in subscriber for {event_type.__name__}: {e}")
    
    def subscribe(self, event_type: Type[IEvent], callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def get_history(self, event_type: Type[IEvent] = None) -> List[IEvent]:
        """Get event history"""
        if event_type:
            return [e for e in self.event_history 
                    if isinstance(e, event_type)]
        return self.event_history