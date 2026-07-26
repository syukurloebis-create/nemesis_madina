# backend/security/auth_handler.py

"""
Auth Handler - Token verification and authentication utilities.
Wrapper functions only - implementation in auth_core.
"""

import os
from typing import Optional, Dict, Any
import logging

# ✅ Import from auth_core (not auth.py) - memutus circular import
from backend.security.auth_core import (
    create_access_token,
    decode_token,
    verify_token,
)

logger = logging.getLogger(__name__)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token (alias for decode_token)."""
    return decode_token(token)


def create_jwt_token(data: Dict[str, Any]) -> str:
    """Create JWT token (alias for create_access_token)."""
    return create_access_token(data)


async def verify_websocket_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify WebSocket token."""
    return verify_token(token)


__all__ = [
    "verify_token",
    "decode_jwt_token",
    "create_jwt_token",
    "verify_websocket_token",
]