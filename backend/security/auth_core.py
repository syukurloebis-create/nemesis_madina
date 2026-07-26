# backend/security/auth_core.py

"""
Authentication Core - Pure security functions.
No FastAPI, no HTTP dependencies.
Single source of truth for JWT operations.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import os
import hashlib

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


# --- JWT Token Operations ---
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Alias for decode_token - legacy compatibility."""
    return decode_token(token)


# --- User Database (Runtime only) ---
_users_db = {
    "admin@nemesis.com": {
        "id": "admin-001",
        "email": "admin@nemesis.com",
        "hashed_password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
        "role": "admin",
        "full_name": "System Administrator"
    },
    "auditor@apip.go.id": {
        "id": "auditor-001",
        "email": "auditor@apip.go.id",
        "hashed_password": "e38ad214943daad1d64c102faec9de6afea8f4ef5c9af6b1d3f5e0f0b2c0e3b9",
        "role": "auditor",
        "full_name": "APIP Auditor"
    },
    "bpk@bpk.go.id": {
        "id": "bpk-001",
        "email": "bpk@bpk.go.id",
        "hashed_password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
        "role": "examiner",
        "full_name": "BPK Examiner"
    }
}


def get_user(email: str) -> Optional[Dict]:
    """Get user by email - returns user without password hash."""
    user = _users_db.get(email)
    if user:
        return {k: v for k, v in user.items() if k != "hashed_password"}
    return None


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user - called only at runtime."""
    user = _users_db.get(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {k: v for k, v in user.items() if k != "hashed_password"}


def verify_api_key(api_key: str) -> Optional[Dict]:
    """Verify API key for external system."""
    valid_keys = {
        "apip_key_2024": {"organization": "APIP", "allowed_endpoints": ["/ml/*", "/findings/*"]},
        "bpk_key_2024": {"organization": "BPK", "allowed_endpoints": ["/audit/*", "/evidence/*"]},
        "bpkp_key_2024": {"organization": "BPKP", "allowed_endpoints": ["/webhooks/*", "/findings/*"]}
    }
    return valid_keys.get(api_key)


def verify_hash_chain(events):
    """Legacy compatibility wrapper for verify_hash_chain."""
    from backend.cases.hash_engine import verify_hash_chain as _verify
    return _verify(events)


__all__ = [
    # Password
    "hash_password",
    "verify_password",
    # JWT
    "create_access_token",
    "decode_token",
    "verify_token",
    # User
    "get_user",
    "authenticate_user",
    "verify_api_key",
    "verify_hash_chain", 
]