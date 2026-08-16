"""
Outbox Event Serializer
Contract: Serialize/deserialize domain events for outbox pattern

Part of Infrastructure Layer
Dependency: None (pure serialization)
Consumer: OutboxPublisher, EventStore
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


class OutboxSerializer:
    """
    Serializer for outbox pattern events.
    
    Contract: 
    - serialize: DomainEvent → Dict with metadata
    - deserialize: Dict → DomainEvent payload
    - Version: 1.0
    - Immutable, stateless
    """
    
    @staticmethod
    def serialize(event: Any) -> Dict[str, Any]:
        """
        Serialize domain event to outbox format.
        
        Args:
            event: DomainEvent instance
            
        Returns:
            Dict with event_id, event_type, occurred_at, payload, metadata
        """
        # Handle event_id as UUID or string
        event_id = str(event.event_id) if hasattr(event, 'event_id') else None
        
        # Handle occurred_at as datetime or string
        occurred_at = None
        if hasattr(event, 'occurred_at') and event.occurred_at:
            if isinstance(event.occurred_at, datetime):
                occurred_at = event.occurred_at.isoformat()
            else:
                occurred_at = str(event.occurred_at)
        
        # Extract payload
        payload = {}
        if hasattr(event, 'payload'):
            payload = event.payload if isinstance(event.payload, dict) else {}
        elif hasattr(event, 'dict'):
            # For Pydantic models
            try:
                payload = event.dict()
            except:
                payload = {}
        
        # Build outbox record
        return {
            "event_id": event_id,
            "event_type": getattr(event, 'event_type', 'UNKNOWN'),
            "occurred_at": occurred_at,
            "payload": payload,
            "metadata": {
                "version": "1.0",
                "serializer": "OutboxSerializer",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def deserialize(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize outbox data for processing.
        
        Args:
            data: Dict from outbox storage
            
        Returns:
            Dict with deserialized event data
        """
        result = {
            "event_id": data.get("event_id"),
            "event_type": data.get("event_type"),
            "payload": data.get("payload", {}),
            "metadata": data.get("metadata", {})
        }
        
        # Parse occurred_at if present
        if data.get("occurred_at"):
            try:
                result["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
            except (ValueError, TypeError):
                result["occurred_at"] = None
        
        return result
    
    @staticmethod
    def serialize_batch(events: list) -> list:
        """Serialize multiple events."""
        return [OutboxSerializer.serialize(event) for event in events]
    
    @staticmethod
    def deserialize_batch(data_list: list) -> list:
        """Deserialize multiple records."""
        return [OutboxSerializer.deserialize(data) for data in data_list]
