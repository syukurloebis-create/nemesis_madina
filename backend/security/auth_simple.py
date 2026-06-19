"""Authentication - Simplified for development (NO bcrypt)"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
import uuid
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Simple password hashing (SHA256) - NO bcrypt
def simple_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

users_db = {
    "admin@nemesis.com": {
        "id": str(uuid.uuid4()),
        "email": "admin@nemesis.com",
        "hashed_password": simple_hash("admin123"),
        "role": "admin",
        "full_name": "System Administrator"
    },
    "auditor@apip.go.id": {
        "id": str(uuid.uuid4()),
        "email": "auditor@apip.go.id",
        "hashed_password": simple_hash("audit123"),
        "role": "auditor",
        "full_name": "APIP Auditor"
    }
}

def verify_password(plain: str, hashed: str) -> bool:
    return simple_hash(plain) == hashed

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    user = users_db.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return {k: v for k, v in user.items() if k != "hashed_password"}

def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = users_db.get(email)
        if not user:
            raise HTTPException(401, "User not found")
        return {k: v for k, v in user.items() if k != "hashed_password"}
    except JWTError:
        raise HTTPException(401, "Invalid token")

def require_role(required_role: str):
    async def checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") != required_role and current_user.get("role") != "admin":
            raise HTTPException(403, f"Role {required_role} required")
        return current_user
    return checker

def verify_api_key(api_key: str):
    """Verify API key for external system integration"""
    # Simple validation - replace with real logic
    valid_keys = ["apip_key_2024", "bpk_key_2024", "bpkp_key_2024"]
    return api_key in valid_keys
