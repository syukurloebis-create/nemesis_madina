# backend/security/auth_handler.py
"""
JWT Token Handler - Compatible with existing auth system
"""
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# ============================================
# IMPORT FROM EXISTING AUTH SYSTEM
# ============================================

from backend.security.auth import create_access_token, decode_token

# ============================================
# WEBSOCKET TOKEN VERIFICATION
# ============================================

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifikasi token untuk WebSocket connection.
    Menggunakan decode_token yang sudah ada di sistem.
    """
    try:
        payload = decode_token(token)
        if payload:
            logger.debug(f"Token verified for user: {payload.get('username')}")
        return payload
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None


async def verify_websocket_token(token: str) -> Optional[Dict[str, Any]]:
    """Async wrapper for verify_token"""
    return verify_token(token)


# Alias for compatibility
def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Alias untuk decode_token"""
    try:
        return decode_token(token)
    except Exception:
        return None


def create_jwt_token(data: Dict[str, Any]) -> str:
    """Alias untuk create_access_token"""
    return create_access_token(data)