"""Authentication Core - Lazy initialization, no import-time hashing"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
import uuid
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Simple password hashing (SHA256) - NO bcrypt, NO import-time execution
def simple_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# User database - store pre-computed hashes (no hashing at import)
_users_db = {
    "admin@nemesis.com": {
        "id": "admin-001",
        "email": "admin@nemesis.com",
        "hashed_password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # "admin123"
        "role": "admin",
        "full_name": "System Administrator"
    },
    "auditor@apip.go.id": {
        "id": "auditor-001", 
        "email": "auditor@apip.go.id",
        "hashed_password": "e38ad214943daad1d64c102faec9de6afea8f4ef5c9af6b1d3f5e0f0b2c0e3b9",  # "audit123"
        "role": "auditor",
        "full_name": "APIP Auditor"
    },
    "bpk@bpk.go.id": {
        "id": "bpk-001",
        "email": "bpk@bpk.go.id", 
        "hashed_password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",  # "bpk123"
        "role": "examiner",
        "full_name": "BPK Examiner"
    }
}


def get_user(email: str) -> Optional[Dict]:
    """Get user by email - no hashing at import"""
    user = _users_db.get(email)
    if user:
        return {k: v for k, v in user.items() if k != "hashed_password"}
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - simple SHA256 comparison"""
    return simple_hash(plain_password) == hashed_password


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user - called only at runtime"""
    user = _users_db.get(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {k: v for k, v in user.items() if k != "hashed_password"}


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(email)
    if user is None:
        raise credentials_exception
    return user


def require_role(required_role: str):
    """Role-based access control decorator"""
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") != required_role and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail=f"Role {required_role} required")
        return current_user
    return role_checker


def verify_api_key(api_key: str) -> Optional[Dict]:
    """Verify API key for external system - pure function, no side effects"""
    valid_keys = {
        "apip_key_2024": {"organization": "APIP", "allowed_endpoints": ["/ml/*", "/findings/*"]},
        "bpk_key_2024": {"organization": "BPK", "allowed_endpoints": ["/audit/*", "/evidence/*"]},
        "bpkp_key_2024": {"organization": "BPKP", "allowed_endpoints": ["/webhooks/*", "/findings/*"]}
    }
    return valid_keys.get(api_key)
