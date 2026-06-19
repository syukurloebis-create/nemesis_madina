#!/usr/bin/env python3
"""
NEMESIS FASE 1 - Event Bus Canonicalization
Membuat single source of truth untuk event processing
"""

import sys
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EVENTS_DIR = PROJECT_ROOT / "backend" / "core" / "events"

def create_events_directory():
    """Buat struktur direktori events"""
    print("\n📁 Creating events directory structure...")
    
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buat __init__.py
    init_file = EVENTS_DIR / "__init__.py"
    init_content = '''"""
NEMESIS Event Bus - Single Source of Truth
===========================================
Modul ini adalah canonical source untuk event processing.

Exports:
    - EventBus: Core event bus
    - EventDispatcher: Event dispatching
    - EventRouter: Routing logic
    - SubscriptionManager: Subscription management
"""

from backend.core.events.bus import EventBus
from backend.core.events.dispatcher import EventDispatcher
from backend.core.events.router import EventRouter
from backend.core.events.subscriptions import SubscriptionManager
from backend.core.events.serializer import EventSerializer
from backend.core.events.replay import ReplayEngine
from backend.core.events.dead_letter import DeadLetterQueue

__all__ = [
    'EventBus',
    'EventDispatcher',
    'EventRouter',
    'SubscriptionManager',
    'EventSerializer',
    'ReplayEngine',
    'DeadLetterQueue'
]
'''
    init_file.write_text(init_content)
    print(f"  ✅ Created: {init_file}")
    return True

def create_bus():
    """Buat bus.py - core event bus"""
    content = '''"""
Event Bus - Core Event Processing
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field

from backend.core.events.dispatcher import EventDispatcher
from backend.core.events.subscriptions import SubscriptionManager
from backend.core.events.router import EventRouter
from backend.core.events.dead_letter import DeadLetterQueue


@dataclass
class Event:
    """Domain event"""
    id: str
    type: str
    data: Any
    source: str
    timestamp: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Central event bus - SINGLETON"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.dispatcher = EventDispatcher()
        self.subscription_manager = SubscriptionManager()
        self.router = EventRouter()
        self.dead_letter = DeadLetterQueue()
        self._event_history: List[Event] = []
        self._max_history = 10000
        self._initialized = True
    
    async def publish(self, event: Event) -> bool:
        """Publish event to all subscribers"""
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Route event
        target_handlers = self.router.route(event.type)
        
        # Dispatch to handlers
        try:
            results = await self.dispatcher.dispatch(event, target_handlers)
            return all(results.values())
        except Exception as e:
            await self.dead_letter.enqueue(event, str(e))
            return False
    
    def subscribe(self, event_type: str, handler: Callable, priority: int = 0):
        """Subscribe handler to event type"""
        self.subscription_manager.add(event_type, handler, priority)
        self.router.register(event_type, handler, priority)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe handler from event type"""
        self.subscription_manager.remove(event_type, handler)
        self.router.unregister(event_type, handler)
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get event history"""
        if event_type:
            filtered = [e for e in self._event_history if e.type == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
    
    async def replay(self, from_timestamp: datetime, to_timestamp: datetime) -> Dict[str, Any]:
        """Replay events in time range"""
        events = [
            e for e in self._event_history
            if from_timestamp <= e.timestamp <= to_timestamp
        ]
        
        results = {"total": len(events), "success": 0, "failed": 0}
        
        for event in events:
            success = await self.publish(event)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return {
            "total_events_processed": len(self._event_history),
            "active_subscriptions": self.subscription_manager.count(),
            "dead_letter_size": self.dead_letter.size(),
            "routing_table_size": self.router.size()
        }
'''
    
    file_path = EVENTS_DIR / "bus.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_dispatcher():
    """Buat dispatcher.py - event dispatching"""
    content = '''"""
Event Dispatcher - Dispatch events to handlers
"""

import asyncio
from typing import Dict, List, Any, Callable
from dataclasses import dataclass


@dataclass
class DispatchResult:
    """Result of event dispatch"""
    handler_name: str
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0


class EventDispatcher:
    """Dispatch events to registered handlers"""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def dispatch(self, event: Any, handlers: List[Callable]) -> Dict[str, bool]:
        """Dispatch event to multiple handlers"""
        results = {}
        
        async def dispatch_one(handler):
            async with self._semaphore:
                result = DispatchResult(handler_name=handler.__name__, success=False)
                import time
                start = time.perf_counter()
                
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                    result.success = True
                except Exception as e:
                    result.error = str(e)
                finally:
                    result.duration_ms = (time.perf_counter() - start) * 1000
                    results[handler.__name__] = result.success
                    
                    # Log slow handlers
                    if result.duration_ms > 100:
                        print(f"Slow handler: {handler.__name__} took {result.duration_ms:.2f}ms")
        
        # Dispatch to all handlers concurrently
        tasks = [dispatch_one(handler) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def dispatch_sequential(self, event: Any, handlers: List[Callable]) -> Dict[str, bool]:
        """Dispatch event to handlers sequentially"""
        results = {}
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                results[handler.__name__] = True
            except Exception as e:
                results[handler.__name__] = False
        
        return results
'''
    
    file_path = EVENTS_DIR / "dispatcher.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_router():
    """Buat router.py - event routing"""
    content = '''"""
Event Router - Route events to handlers
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict


class EventRouter:
    """Route events to appropriate handlers"""
    
    def __init__(self):
        self._routes: Dict[str, List[tuple]] = defaultdict(list)  # event_type -> [(priority, handler)]
    
    def register(self, event_type: str, handler: Callable, priority: int = 0):
        """Register handler for event type"""
        self._routes[event_type].append((priority, handler))
        # Sort by priority (higher priority first)
        self._routes[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def unregister(self, event_type: str, handler: Callable):
        """Unregister handler from event type"""
        self._routes[event_type] = [
            (p, h) for p, h in self._routes[event_type] if h != handler
        ]
    
    def route(self, event_type: str) -> List[Callable]:
        """Get handlers for event type"""
        return [handler for _, handler in self._routes.get(event_type, [])]
    
    def route_wildcard(self, event_type: str) -> List[Callable]:
        """Get handlers for wildcard subscriptions"""
        wildcard_handlers = []
        
        for route_type, handlers in self._routes.items():
            if route_type.endswith("*"):
                prefix = route_type[:-1]
                if event_type.startswith(prefix):
                    wildcard_handlers.extend([h for _, h in handlers])
        
        return wildcard_handlers
    
    def clear(self):
        """Clear all routes"""
        self._routes.clear()
    
    def size(self) -> int:
        """Get total number of route entries"""
        return sum(len(handlers) for handlers in self._routes.values())
    
    def get_routes(self) -> Dict[str, List[str]]:
        """Get all registered routes"""
        return {
            event_type: [h.__name__ for _, h in handlers]
            for event_type, handlers in self._routes.items()
        }
'''
    
    file_path = EVENTS_DIR / "router.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_subscriptions():
    """Buat subscriptions.py - subscription management"""
    content = '''"""
Subscription Manager - Manage event subscriptions
"""

from typing import Dict, Set, Callable, Any
from collections import defaultdict


class SubscriptionManager:
    """Manage event subscriptions"""
    
    def __init__(self):
        self._subscriptions: Dict[str, Set[Callable]] = defaultdict(set)
    
    def add(self, event_type: str, handler: Callable, priority: int = 0):
        """Add subscription"""
        self._subscriptions[event_type].add(handler)
    
    def remove(self, event_type: str, handler: Callable):
        """Remove subscription"""
        if event_type in self._subscriptions:
            self._subscriptions[event_type].discard(handler)
    
    def get(self, event_type: str) -> Set[Callable]:
        """Get subscribers for event type"""
        return self._subscriptions.get(event_type, set())
    
    def has_subscriber(self, event_type: str, handler: Callable) -> bool:
        """Check if handler is subscribed"""
        return handler in self._subscriptions.get(event_type, set())
    
    def count(self) -> int:
        """Get total number of subscriptions"""
        return sum(len(handlers) for handlers in self._subscriptions.values())
    
    def count_by_type(self, event_type: str) -> int:
        """Get number of subscribers for event type"""
        return len(self._subscriptions.get(event_type, set()))
    
    def get_all(self) -> Dict[str, Set[Callable]]:
        """Get all subscriptions"""
        return dict(self._subscriptions)
    
    def clear(self):
        """Clear all subscriptions"""
        self._subscriptions.clear()
    
    def remove_all_for_handler(self, handler: Callable):
        """Remove all subscriptions for a specific handler"""
        for event_type in list(self._subscriptions.keys()):
            self._subscriptions[event_type].discard(handler)
    
    def get_stats(self) -> dict:
        """Get subscription statistics"""
        return {
            "total_subscriptions": self.count(),
            "event_types": len(self._subscriptions),
            "avg_per_type": self.count() / len(self._subscriptions) if self._subscriptions else 0
        }
'''
    
    file_path = EVENTS_DIR / "subscriptions.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_serializer():
    """Buat serializer.py - event serialization"""
    content = '''"""
Event Serializer - Serialize/Deserialize events
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from backend.core.events.bus import Event


class EventSerializer:
    """Serialize and deserialize events"""
    
    @staticmethod
    def serialize(event: Event) -> str:
        """Serialize event to JSON string"""
        data = {
            "id": event.id,
            "type": event.type,
            "data": event.data,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "correlation_id": event.correlation_id,
            "causation_id": event.causation_id,
            "metadata": event.metadata
        }
        return json.dumps(data, default=str)
    
    @staticmethod
    def deserialize(json_str: str) -> Event:
        """Deserialize event from JSON string"""
        data = json.loads(json_str)
        
        return Event(
            id=data["id"],
            type=data["type"],
            data=data["data"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            metadata=data.get("metadata", {})
        )
    
    @staticmethod
    def to_dict(event: Event) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "id": event.id,
            "type": event.type,
            "data": event.data,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "correlation_id": event.correlation_id,
            "causation_id": event.causation_id,
            "metadata": event.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Event:
        """Create event from dictionary"""
        return Event(
            id=data["id"],
            type=data["type"],
            data=data["data"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            metadata=data.get("metadata", {})
        )
'''
    
    file_path = EVENTS_DIR / "serializer.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_replay():
    """Buat replay.py - replay engine"""
    content = '''"""
Replay Engine - Event replay functionality
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.core.events.bus import EventBus, Event


class ReplayEngine:
    """Engine for replaying historical events"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    async def replay_by_type(self, event_type: str, limit: int = 1000) -> Dict[str, Any]:
        """Replay events of specific type"""
        history = self.event_bus.get_history(event_type, limit)
        
        results = {"total": len(history), "success": 0, "failed": 0, "events": []}
        
        for event in history:
            success = await self.event_bus.publish(event)
            if success:
                results["success"] += 1
                results["events"].append({"id": event.id, "status": "success"})
            else:
                results["failed"] += 1
                results["events"].append({"id": event.id, "status": "failed"})
        
        return results
    
    async def replay_by_source(self, source: str, limit: int = 1000) -> Dict[str, Any]:
        """Replay events from specific source"""
        history = self.event_bus.get_history(limit=limit * 2)
        
        filtered = [e for e in history if e.source == source][:limit]
        
        results = {"total": len(filtered), "success": 0, "failed": 0}
        
        for event in filtered:
            success = await self.event_bus.publish(event)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    async def replay_with_transform(
        self,
        events: List[Event],
        transform_fn: callable
    ) -> Dict[str, Any]:
        """Replay events with transformation"""
        results = {"total": len(events), "success": 0, "failed": 0}
        
        for event in events:
            try:
                transformed = transform_fn(event)
                if transformed:
                    success = await self.event_bus.publish(transformed)
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
            except Exception:
                results["failed"] += 1
        
        return results
'''
    
    file_path = EVENTS_DIR / "replay.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_dead_letter():
    """Buat dead_letter.py - dead letter queue"""
    content = '''"""
Dead Letter Queue - Handle failed events
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque


class DeadLetterQueue:
    """Queue for events that failed processing"""
    
    def __init__(self, max_size: int = 1000):
        self._queue: deque = deque(maxlen=max_size)
        self._lock = asyncio.Lock()
    
    async def enqueue(self, event: Any, reason: str):
        """Add failed event to queue"""
        async with self._lock:
            self._queue.append({
                "event": event,
                "reason": reason,
                "failed_at": datetime.now(),
                "retry_count": 0
            })
    
    async def dequeue(self) -> Optional[Dict]:
        """Get next failed event"""
        async with self._lock:
            if self._queue:
                return self._queue.popleft()
        return None
    
    async def retry_all(self, retry_fn: callable) -> Dict[str, int]:
        """Retry all failed events"""
        results = {"success": 0, "failed": 0}
        
        while True:
            item = await self.dequeue()
            if not item:
                break
            
            try:
                success = await retry_fn(item["event"])
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    # Re-queue with incremented retry count
                    item["retry_count"] += 1
                    if item["retry_count"] < 3:
                        await self.enqueue(item["event"], f"Retry {item['retry_count']}")
            except Exception:
                results["failed"] += 1
        
        return results
    
    def size(self) -> int:
        """Get queue size"""
        return len(self._queue)
    
    def clear(self):
        """Clear the queue"""
        self._queue.clear()
    
    def peek(self, limit: int = 10) -> List[Dict]:
        """Peek at queue without removing"""
        return list(self._queue)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "size": self.size(),
            "max_size": self._queue.maxlen,
            "events": self.peek(5)
        }
'''
    
    file_path = EVENTS_DIR / "dead_letter.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 1: EVENT BUS CANONICALIZATION")
    print("="*60)
    
    success = True
    success &= create_events_directory()
    success &= create_bus()
    success &= create_dispatcher()
    success &= create_router()
    success &= create_subscriptions()
    success &= create_serializer()
    success &= create_replay()
    success &= create_dead_letter()
    
    print("\n" + "="*60)
    if success:
        print("✅ EVENT BUS CANONICALIZATION COMPLETE")
        print(f"   Location: {EVENTS_DIR}")
    else:
        print("❌ EVENT BUS CANONICALIZATION FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())