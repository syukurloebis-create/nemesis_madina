#!/bin/bash
# ============================================================================
# NEMESIS FASE 1 - Auto Fix Script
# ============================================================================

cd ~/nemesis_madina

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS FASE 1 - AUTO FIX SCRIPT                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Fix 1: Add missing imports to event bus files
echo "[1/4] Fixing missing imports in event bus..."

# Fix dispatcher.py
if grep -q "Optional" backend/core/events/dispatcher.py 2>/dev/null; then
    if ! grep -q "from typing import.*Optional" backend/core/events/dispatcher.py; then
        sed -i 's/from typing import Dict, List, Any, Callable/from typing import Dict, List, Any, Callable, Optional/g' backend/core/events/dispatcher.py
        echo "  ✅ Fixed dispatcher.py imports"
    fi
fi

# Fix bus.py imports
if ! grep -q "from typing import.*Optional" backend/core/events/bus.py; then
    sed -i 's/from typing import Dict, List, Any, Callable, Set/from typing import Dict, List, Any, Callable, Set, Optional/g' backend/core/events/bus.py
    echo "  ✅ Fixed bus.py imports"
fi

# Fix dead_letter.py imports
cat > backend/core/events/dead_letter.py << 'DEADEOF'
"""
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
DEADEOF
echo "  ✅ Fixed dead_letter.py"

# Fix replay.py imports
cat > backend/core/events/replay.py << 'REPLAYEOF'
"""
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
REPLAYEOF
echo "  ✅ Fixed replay.py"

# Fix serializer.py
cat > backend/core/events/serializer.py << 'SEREOF'
"""
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
SEREOF
echo "  ✅ Fixed serializer.py"

# Fix 2: Apply all import updates
echo ""
echo "[2/4] Applying import updates..."

# Update all Python files
find backend tests -name "*.py" -type f 2>/dev/null | while read file; do
    # Evidence imports
    sed -i 's/from backend\.evidence_registry import/from backend.evidence.registry import/g' "$file"
    sed -i 's/from backend\.evidence_hashing import/from backend.evidence.hashing import/g' "$file"
    sed -i 's/from backend\.intelligence\.legal\.evidence_registry import/from backend.evidence.registry import/g' "$file"
    sed -i 's/from backend\.intelligence\.legal\.evidence_hashing import/from backend.evidence.hashing import/g' "$file"
    
    # WebSocket imports
    sed -i 's/from backend\.ws\.gateway import/from backend.websocket.manager import/g' "$file"
    sed -i 's/from backend\.ws\.event_bus import/from backend.websocket.broadcaster import/g' "$file"
    sed -i 's/from backend\.websocket\.connection_manager import/from backend.websocket.manager import/g' "$file"
    
    # Event bus imports
    sed -i 's/from backend\.core\.events\.event_bus import/from backend.core.events.bus import/g' "$file"
    sed -i 's/from backend\.orchestrator\.event_bus_v2 import/from backend.core.events.bus import/g' "$file"
    
    # Graph imports
    sed -i 's/from backend\.intelligence\.graph\.relationship_graph import/from backend.graph.relationship_graph import/g' "$file"
    sed -i 's/from backend\.intelligence\.core\.graph\.relationship_graph import/from backend.graph.relationship_graph import/g' "$file"
    sed -i 's/from backend\.intelligence\.graph\.collusion_detector import/from backend.graph.collusion_detector import/g' "$file"
    sed -i 's/from backend\.intelligence\.core\.graph\.collusion_detector import/from backend.graph.collusion_detector import/g' "$file"
    
    # Remove duplicate __pycache__ references
    if [ -f "$file" ]; then
        echo -n ""
    fi
done

echo "  ✅ Import updates applied"

# Fix 3: Clean up duplicates
echo ""
echo "[3/4] Cleaning up duplicates..."

# Remove duplicate __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove duplicate .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "  ✅ Cache cleaned"

# Fix 4: Run verification
echo ""
echo "[4/4] Running verification..."

python scripts/fase1/06_verify_canonical.py

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 1 AUTO FIX COMPLETE                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
