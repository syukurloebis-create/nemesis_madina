#!/usr/bin/env python3
"""
NEMESIS FASE 3 - Enhance Event Replay Engine with Snapshots
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
import json

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EVENTS_DIR = PROJECT_ROOT / "backend" / "core" / "events"

def create_snapshots():
    """Create snapshots.py for event snapshots"""
    print("\n[1/2] Creating snapshots module...")
    
    content = '''"""
Event Snapshots - Snapshot Management for Fast Recovery
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class EventSnapshot:
    """Snapshot of event state for fast recovery"""
    
    def __init__(self, snapshot_dir: Path = None):
        self.snapshot_dir = snapshot_dir or Path("./snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._current_snapshot: Optional[Dict[str, Any]] = None
    
    def create_snapshot(self, event_bus_state: Dict[str, Any], snapshot_id: str = None) -> str:
        """Create a snapshot of current state"""
        if snapshot_id is None:
            snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        snapshot = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "state": event_bus_state,
            "event_count": len(event_bus_state.get('events', []))
        }
        
        # Save to file
        snapshot_file = self.snapshot_dir / f"snapshot_{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        self._current_snapshot = snapshot
        return snapshot_id
    
    def load_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Load a snapshot from file"""
        snapshot_file = self.snapshot_dir / f"snapshot_{snapshot_id}.json"
        if not snapshot_file.exists():
            return None
        
        with open(snapshot_file, 'r') as f:
            return json.load(f)
    
    def load_latest(self) -> Optional[Dict[str, Any]]:
        """Load the latest snapshot"""
        snapshots = list(self.snapshot_dir.glob("snapshot_*.json"))
        if not snapshots:
            return None
        
        latest = max(snapshots, key=lambda p: p.stat().st_mtime)
        with open(latest, 'r') as f:
            return json.load(f)
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots"""
        snapshots = []
        for snapshot_file in sorted(self.snapshot_dir.glob("snapshot_*.json")):
            with open(snapshot_file, 'r') as f:
                data = json.load(f)
                snapshots.append({
                    "id": data.get("snapshot_id"),
                    "timestamp": data.get("timestamp"),
                    "event_count": data.get("event_count", 0)
                })
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        snapshot_file = self.snapshot_dir / f"snapshot_{snapshot_id}.json"
        if snapshot_file.exists():
            snapshot_file.unlink()
            return True
        return False
    
    def cleanup_old_snapshots(self, keep_count: int = 10):
        """Delete old snapshots, keeping only the most recent ones"""
        snapshots = sorted(self.snapshot_dir.glob("snapshot_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        for old_snapshot in snapshots[keep_count:]:
            old_snapshot.unlink()
    
    def get_current(self) -> Optional[Dict[str, Any]]:
        """Get current snapshot"""
        return self._current_snapshot
'''
    
    file_path = EVENTS_DIR / "snapshots.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def enhance_replay_engine():
    """Enhance replay.py with snapshot support"""
    print("\n[2/2] Enhancing replay engine...")
    
    replay_path = EVENTS_DIR / "replay.py"
    
    if replay_path.exists():
        # Read existing content
        with open(replay_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add snapshot import if not exists
        if 'from backend.core.events.snapshots import EventSnapshot' not in content:
            content = 'from backend.core.events.snapshots import EventSnapshot\n' + content
        
        # Add snapshot methods
        if 'create_snapshot' not in content:
            snapshot_methods = '''
    
    async def create_snapshot(self) -> str:
        """Create a snapshot of current state"""
        snapshot = EventSnapshot()
        state = {
            "events": self.event_bus.get_history(limit=1000),
            "timestamp": datetime.now().isoformat()
        }
        return snapshot.create_snapshot(state)
    
    async def restore_from_snapshot(self, snapshot_id: str = None) -> bool:
        """Restore state from snapshot"""
        snapshot = EventSnapshot()
        
        if snapshot_id:
            state = snapshot.load_snapshot(snapshot_id)
        else:
            state = snapshot.load_latest()
        
        if not state:
            return False
        
        # Restore events
        for event_data in state.get('state', {}).get('events', []):
            from backend.core.events.bus import Event
            event = Event(
                id=event_data.get('id'),
                type=event_data.get('type'),
                data=event_data.get('data'),
                source=event_data.get('source'),
                timestamp=datetime.fromisoformat(event_data.get('timestamp'))
            )
            await self.event_bus.publish(event)
        
        return True
'''
            # Find where to insert (before the last method)
            lines = content.split('\n')
            insert_pos = len(lines) - 2
            for i, line in enumerate(lines):
                if 'def get_metrics' in line:
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, snapshot_methods)
            content = '\n'.join(lines)
        
        replay_path.write_text(content)
        print(f"  [OK] Enhanced: {replay_path}")
    else:
        # Create new replay.py
        content = '''"""
Replay Engine - Event replay functionality with snapshots
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.core.events.bus import EventBus, Event
from backend.core.events.snapshots import EventSnapshot


class ReplayEngine:
    """Engine for replaying historical events"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    async def replay_by_type(self, event_type: str, limit: int = 1000) -> Dict[str, Any]:
        """Replay events of specific type"""
        history = self.event_bus.get_history(event_type, limit)
        
        results = {"total": len(history), "success": 0, "failed": 0}
        
        for event in history:
            success = await self.event_bus.publish(event)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    async def replay_by_range(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Replay events in time range"""
        history = self.event_bus.get_history(limit=10000)
        filtered = [e for e in history if start <= e.timestamp <= end]
        
        results = {"total": len(filtered), "success": 0, "failed": 0}
        
        for event in filtered:
            success = await self.event_bus.publish(event)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    async def create_snapshot(self) -> str:
        """Create a snapshot of current state"""
        snapshot = EventSnapshot()
        state = {
            "events": [self._event_to_dict(e) for e in self.event_bus.get_history(limit=1000)],
            "timestamp": datetime.now().isoformat()
        }
        return snapshot.create_snapshot(state)
    
    async def restore_from_snapshot(self, snapshot_id: str = None) -> bool:
        """Restore state from snapshot"""
        snapshot = EventSnapshot()
        
        if snapshot_id:
            state = snapshot.load_snapshot(snapshot_id)
        else:
            state = snapshot.load_latest()
        
        if not state:
            return False
        
        # Clear current events
        self.event_bus.clear_history()
        
        # Restore events
        for event_dict in state.get('state', {}).get('events', []):
            event = self._dict_to_event(event_dict)
            await self.event_bus.publish(event)
        
        return True
    
    def _event_to_dict(self, event: Event) -> Dict[str, Any]:
        return {
            "id": event.id,
            "type": event.type,
            "data": event.data,
            "source": event.source,
            "timestamp": event.timestamp.isoformat()
        }
    
    def _dict_to_event(self, data: Dict[str, Any]) -> Event:
        return Event(
            id=data["id"],
            type=data["type"],
            data=data["data"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
'''
        replay_path.write_text(content)
        print(f"  [OK] Created: {replay_path}")
    
    return True

def main():
    print("\n" + "="*60)
    print("FASE 3: ENHANCE REPLAY ENGINE")
    print("="*60)
    
    create_snapshots()
    enhance_replay_engine()
    
    print("\n" + "="*60)
    print("[OK] Replay engine enhanced")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())