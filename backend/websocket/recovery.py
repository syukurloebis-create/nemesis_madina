"""
Recovery Handler - Handle reconnection and state recovery
"""

import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime


class RecoveryHandler:
    """Handle client reconnection and state recovery"""
    
    def __init__(self, connection_manager, broadcaster):
        self.manager = connection_manager
        self.broadcaster = broadcaster
        self._client_state: Dict[str, Dict[str, Any]] = {}
        self._reconnect_attempts: Dict[str, int] = {}
        self._max_attempts = 5
    
    def save_state(self, client_id: str, state: Dict[str, Any]):
        """Save client state for potential recovery"""
        self._client_state[client_id] = {
            "state": state,
            "saved_at": datetime.now(),
            "subscriptions": self.broadcaster._client_subscriptions.get(client_id, set()).copy()
        }
    
    def get_state(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get saved client state"""
        if client_id in self._client_state:
            return self._client_state[client_id]["state"]
        return None
    
    def restore_subscriptions(self, client_id: str):
        """Restore client subscriptions"""
        if client_id in self._client_state:
            subscriptions = self._client_state[client_id].get("subscriptions", set())
            for event_type in subscriptions:
                self.broadcaster.subscribe(client_id, event_type)
    
    async def handle_reconnect(self, old_client_id: str, new_client_id: str) -> bool:
        """Handle client reconnection"""
        if old_client_id not in self._client_state:
            return False
        
        # Restore subscriptions
        self.restore_subscriptions(old_client_id)
        
        # Transfer state
        state = self.get_state(old_client_id)
        if state:
            self.save_state(new_client_id, state)
        
        # Clean up old state
        if old_client_id != new_client_id:
            del self._client_state[old_client_id]
        
        return True
    
    def record_attempt(self, client_id: str):
        """Record reconnection attempt"""
        if client_id not in self._reconnect_attempts:
            self._reconnect_attempts[client_id] = 0
        self._reconnect_attempts[client_id] += 1
    
    def should_allow_reconnect(self, client_id: str) -> bool:
        """Check if client should be allowed to reconnect"""
        attempts = self._reconnect_attempts.get(client_id, 0)
        return attempts < self._max_attempts
    
    def reset_attempts(self, client_id: str):
        """Reset reconnection attempts"""
        if client_id in self._reconnect_attempts:
            del self._reconnect_attempts[client_id]
    
    def cleanup_stale_state(self, max_age_seconds: int = 3600):
        """Clean up stale client state"""
        now = datetime.now()
        stale_ids = []
        
        for client_id, data in self._client_state.items():
            saved_at = data.get("saved_at")
            if saved_at:
                age = (now - saved_at).total_seconds()
                if age > max_age_seconds:
                    stale_ids.append(client_id)
        
        for client_id in stale_ids:
            del self._client_state[client_id]
        
        return len(stale_ids)
