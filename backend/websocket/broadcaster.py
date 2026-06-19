"""
Event Broadcaster - Broadcast events to clients
"""

import asyncio
from typing import Dict, Set, Any, Optional
from collections import defaultdict
from datetime import datetime


class EventBroadcaster:
    """Broadcast events to WebSocket clients"""
    
    def __init__(self, connection_manager):
        self.manager = connection_manager
        self._subscriptions: Dict[str, Set[str]] = defaultdict(set)  # event_type -> client_ids
        self._client_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # client_id -> event_types
    
    def subscribe(self, client_id: str, event_type: str):
        """Subscribe client to event type"""
        self._subscriptions[event_type].add(client_id)
        self._client_subscriptions[client_id].add(event_type)
    
    def unsubscribe(self, client_id: str, event_type: str):
        """Unsubscribe client from event type"""
        self._subscriptions[event_type].discard(client_id)
        self._client_subscriptions[client_id].discard(event_type)
    
    def unsubscribe_all(self, client_id: str):
        """Unsubscribe client from all events"""
        for event_type in self._client_subscriptions.get(client_id, set()):
            self._subscriptions[event_type].discard(client_id)
        self._client_subscriptions[client_id].clear()
    
    async def broadcast_event(self, event_type: str, data: Any, exclude: Set[str] = None):
        """Broadcast event to all subscribed clients"""
        exclude = exclude or set()
        subscribers = self._subscriptions.get(event_type, set())
        targets = subscribers - exclude
        
        if not targets:
            return
        
        message = {
            "type": "event",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to each target
        tasks = []
        for client_id in targets:
            tasks.append(self.manager.send(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_all(self, event_type: str, data: Any):
        """Broadcast to all connected clients regardless of subscription"""
        message = {
            "type": "broadcast",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message)
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type"""
        return len(self._subscriptions.get(event_type, set()))
    
    def get_metrics(self) -> dict:
        """Get broadcaster metrics"""
        return {
            "total_subscriptions": sum(len(s) for s in self._subscriptions.values()),
            "event_types": len(self._subscriptions),
            "subscribers_by_type": {
                k: len(v) for k, v in self._subscriptions.items()
            }
        }
