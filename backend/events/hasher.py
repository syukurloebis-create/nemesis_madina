# backend/events/hasher.py
import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class EventHasher:
    """Event hash calculator for triple hash chain"""
    
    @staticmethod
    def calculate_event_hash(
        event_id: uuid.UUID,
        aggregate_id: uuid.UUID,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Dict[str, Any],
        timestamp: datetime,
        previous_hash: Optional[str] = None
    ) -> str:
        """Calculate individual event hash"""
        block = {
            "event_id": str(event_id),
            "aggregate_id": str(aggregate_id),
            "event_type": event_type,
            "payload": payload,
            "metadata": metadata,
            "timestamp": timestamp.isoformat(),
            "previous_hash": previous_hash
        }
        
        # Canonical JSON with sorted keys
        canonical = json.dumps(block, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    @staticmethod
    def calculate_aggregate_hash(events: list) -> str:
        """Calculate aggregate hash chain"""
        current = "GENESIS_" + hashlib.sha256(b"GENESIS").hexdigest()
        
        for event in sorted(events, key=lambda e: e.get('version', 0)):
            event_hash = event.get('event_hash', '')
            if event_hash:
                current = hashlib.sha256(
                    f"{current}:{event_hash}".encode()
                ).hexdigest()
        
        return current