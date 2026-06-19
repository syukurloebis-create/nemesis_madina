# backend/security/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid

from backend.database import get_db
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint"""
    try:
        # Get user from database
        query = text("""
            SELECT id, username, password_hash, role, is_active 
            FROM users 
            WHERE username = :username
        """)
        result = await db.execute(query, {"username": request.username})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user[2]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if active
        if not user[4]:
            raise HTTPException(status_code=403, detail="Account disabled")
        
        # Create tokens
        access_token = create_access_token({
            "sub": user[1],
            "user_id": str(user[0]),
            "role": user[3]
        })
        
        refresh_token = create_refresh_token({
            "sub": user[1],
            "user_id": str(user[0])
        })
        
        # Log audit action (without using the problematic audit_log for now)
        # We'll add a simple insert directly
        try:
            audit_query = text("""
                INSERT INTO audit_log (id, user_id, action, resource, timestamp)
                VALUES (:id, :user_id, :action, :resource, :timestamp)
            """)
            await db.execute(audit_query, {
                "id": str(uuid.uuid4()),
                "user_id": user[1],
                "action": "LOGIN",
                "resource": "auth",
                "timestamp": datetime.utcnow()
            })
            await db.commit()
        except Exception as audit_error:
            print(f"Audit log error (non-critical): {audit_error}")
            # Don't fail login if audit fails
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))