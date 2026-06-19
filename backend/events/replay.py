# backend/events/replay.py
from typing import List, Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import uuid
import asyncio
from enum import Enum


class ReplayStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReplayTask:
    """Task untuk replay operation"""
    
    def __init__(self, task_id: uuid.UUID, aggregate_id: uuid.UUID, aggregate_type: str):
        self.task_id = task_id
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.status = ReplayStatus.PENDING
        self.progress = 0
        self.total_events = 0
        self.processed_events = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": str(self.task_id),
            "aggregate_id": str(self.aggregate_id),
            "aggregate_type": self.aggregate_type,
            "status": self.status.value,
            "progress": self.progress,
            "total_events": self.total_events,
            "processed_events": self.processed_events,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": (self.end_time - self.start_time).total_seconds() * 1000 if self.start_time and self.end_time else None,
            "error": self.error
        }


class ReplayService:
    """Enhanced replay service untuk event sourcing"""
    
    def __init__(self, event_store):
        self.event_store = event_store
        self._active_tasks: Dict[uuid.UUID, ReplayTask] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register handler untuk event type tertentu"""
        self._handlers[event_type] = handler
    
    async def replay_aggregate(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        target_version: Optional[int] = None,
        from_version: int = 0
    ) -> ReplayTask:
        """Replay aggregate events untuk rebuild state"""
        
        task_id = uuid.uuid4()
        task = ReplayTask(task_id, aggregate_id, aggregate_type)
        self._active_tasks[task_id] = task
        
        task.status = ReplayStatus.RUNNING
        task.start_time = datetime.utcnow()
        
        try:
            # Get events
            events = await self.event_store.get_events(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                from_version=from_version
            )
            
            task.total_events = len(events)
            
            # Rebuild state
            state = {}
            
            for i, event in enumerate(events):
                # Stop if target version reached
                if target_version and event.event_version > target_version:
                    break
                
                # Apply event
                handler = self._handlers.get(event.event_type)
                if handler:
                    await handler(event.payload)
                
                # Apply to state
                state = await self._apply_event_to_state(state, event)
                
                task.processed_events = i + 1
                task.progress = (i + 1) / len(events) * 100
            
            task.status = ReplayStatus.COMPLETED
            task.result = state
            
        except asyncio.CancelledError:
            task.status = ReplayStatus.CANCELLED
            task.error = "Task was cancelled"
        except Exception as e:
            task.status = ReplayStatus.FAILED
            task.error = str(e)
        finally:
            task.end_time = datetime.utcnow()
        
        return task
    
    async def _apply_event_to_state(self, state: Dict[str, Any], event) -> Dict[str, Any]:
        """Apply event ke state"""
        event_type = event.event_type
        payload = event.payload
        
        if event_type == "CASE_CREATED":
            state["title"] = payload.get("title")
            state["description"] = payload.get("description")
            state["priority"] = payload.get("priority", "MEDIUM")
        elif event_type == "CASE_STATUS_CHANGED":
            state["status"] = payload.get("new_status")
        elif event_type == "CASE_PRIORITY_CHANGED":
            state["priority"] = payload.get("new_priority")
        elif event_type == "CASE_ASSIGNED":
            state["assigned_to"] = str(payload.get("assigned_to"))
        elif event_type == "EVIDENCE_ADDED":
            if "evidence" not in state:
                state["evidence"] = []
            state["evidence"].append({
                "id": str(payload.get("evidence_id")),
                "type": payload.get("evidence_type"),
                "filename": payload.get("filename")
            })
        
        return state
    
    async def get_replay_status(self, task_id: uuid.UUID) -> Optional[ReplayTask]:
        """Get status of replay task"""
        return self._active_tasks.get(task_id)
    
    async def cancel_replay(self, task_id: uuid.UUID) -> bool:
        """Cancel running replay task"""
        task = self._active_tasks.get(task_id)
        if task and task.status == ReplayStatus.RUNNING:
            task.status = ReplayStatus.CANCELLED
            return True
        return False
    
    async def get_all_replay_tasks(self, limit: int = 50) -> List[ReplayTask]:
        """Get recent replay tasks"""
        tasks = list(self._active_tasks.values())
        tasks.sort(key=lambda x: x.start_time or datetime.min, reverse=True)
        return tasks[:limit]
    
    async def compare_versions(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        version_a: int,
        version_b: int
    ) -> Dict[str, Any]:
        """Compare two versions of an aggregate"""
        
        state_a = await self.replay_aggregate(
            aggregate_id, aggregate_type, target_version=version_a
        )
        state_b = await self.replay_aggregate(
            aggregate_id, aggregate_type, target_version=version_b
        )
        
        # Wait for completion
        while state_a.status == ReplayStatus.RUNNING:
            await asyncio.sleep(0.1)
        while state_b.status == ReplayStatus.RUNNING:
            await asyncio.sleep(0.1)
        
        # Calculate differences
        differences = []
        all_keys = set((state_a.result or {}).keys()) | set((state_b.result or {}).keys())
        
        for key in all_keys:
            val_a = (state_a.result or {}).get(key)
            val_b = (state_b.result or {}).get(key)
            if val_a != val_b:
                differences.append({
                    "field": key,
                    "from": val_a,
                    "to": val_b
                })
        
        return {
            "aggregate_id": str(aggregate_id),
            "aggregate_type": aggregate_type,
            "version_a": version_a,
            "version_b": version_b,
            "differences": differences,
            "has_changes": len(differences) > 0
        }
    
    async def get_timeline(self, aggregate_id: uuid.UUID, aggregate_type: str) -> List[Dict[str, Any]]:
        """Get timeline of events for an aggregate"""
        
        events = await self.event_store.get_events(aggregate_id, aggregate_type)
        
        timeline = []
        for event in events:
            timeline.append({
                "event_id": str(event.id),
                "event_type": event.event_type,
                "event_version": event.event_version,
                "created_at": event.created_at.isoformat(),
                "created_by": str(event.created_by),
                "payload_summary": {
                    k: v for k, v in event.payload.items()
                    if k not in ["description", "content"]  # Exclude large fields
                }
            })
        
        return timeline