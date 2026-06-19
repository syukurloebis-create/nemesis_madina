"""
Message Protocol - Standard message formats
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class MessageType(str, Enum):
    """Standard message types"""
    PING = "ping"
    PONG = "pong"
    EVENT = "event"
    BROADCAST = "broadcast"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ERROR = "error"
    ACK = "ack"


class MessageProtocol:
    """Standard message protocol for WebSocket communication"""
    
    @staticmethod
    def ping() -> Dict[str, Any]:
        """Create ping message"""
        return {
            "type": MessageType.PING,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def pong() -> Dict[str, Any]:
        """Create pong message"""
        return {
            "type": MessageType.PONG,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def event(event_type: str, data: Any, event_id: Optional[str] = None) -> Dict[str, Any]:
        """Create event message"""
        return {
            "type": MessageType.EVENT,
            "event_type": event_type,
            "data": data,
            "event_id": event_id,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def broadcast(event_type: str, data: Any) -> Dict[str, Any]:
        """Create broadcast message"""
        return {
            "type": MessageType.BROADCAST,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def subscribe(event_types: list) -> Dict[str, Any]:
        """Create subscribe message"""
        return {
            "type": MessageType.SUBSCRIBE,
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def unsubscribe(event_types: list) -> Dict[str, Any]:
        """Create unsubscribe message"""
        return {
            "type": MessageType.UNSUBSCRIBE,
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ack(message_id: str, status: str = "ok") -> Dict[str, Any]:
        """Create acknowledgment message"""
        return {
            "type": MessageType.ACK,
            "message_id": message_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: Optional[int] = None) -> Dict[str, Any]:
        """Create error message"""
        result = {
            "type": MessageType.ERROR,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if code:
            result["code"] = code
        return result
    
    @staticmethod
    def is_valid(message: Dict[str, Any]) -> bool:
        """Validate message format"""
        if "type" not in message:
            return False
        
        msg_type = message["type"]
        if msg_type not in [t.value for t in MessageType]:
            return False
        
        return True
