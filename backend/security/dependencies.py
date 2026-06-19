"""
Dependency Injection for Authentication - Fixed
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nemesis-secret-key-change-in-production")
ALGORITHM = "HS256"


def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "id": user_id,
        "username": username,
        "role": role
    }


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Get current active user"""
    return current_user


def require_role(required_roles: list):
    """Dependency factory for role-based access control (SYNC)"""
    async def role_checker(
        current_user = Depends(get_current_user)
    ):
        if current_user.get("role") not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role {required_roles} required"
            )
        return current_user
    return role_checker
